"""
Event Bus System

This module implements an event-driven communication system that allows
modules to communicate without direct dependencies.
"""

import asyncio
import inspect
import logging
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor


class EventPriority(Enum):
    """Event priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """Represents an event in the system"""
    name: str
    data: Dict[str, Any]
    source: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = EventPriority.NORMAL
    event_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'name': self.name,
            'data': self.data,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority.value,
            'event_id': self.event_id
        }


@dataclass
class EventHandler:
    """Represents an event handler registration"""
    callback: Callable
    event_pattern: str
    priority: EventPriority = EventPriority.NORMAL
    is_async: bool = False
    once: bool = False
    
    def matches(self, event_name: str) -> bool:
        """Check if this handler matches the event name"""
        if self.event_pattern == "*":
            return True
        
        # Support wildcards like "user.*" or "*.created"
        if "*" in self.event_pattern:
            pattern_parts = self.event_pattern.split(".")
            event_parts = event_name.split(".")
            
            if len(pattern_parts) != len(event_parts):
                return False
            
            for pattern_part, event_part in zip(pattern_parts, event_parts):
                if pattern_part != "*" and pattern_part != event_part:
                    return False
            return True
        
        return self.event_pattern == event_name


class EventBus:
    """
    Central event bus for module communication.
    
    Supports both synchronous and asynchronous event handlers,
    wildcards, priorities, and one-time handlers.
    """
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize the event bus.
        
        Args:
            max_workers: Maximum number of worker threads for async execution
        """
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._logger = logging.getLogger(__name__)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.RLock()
        
    def on(self, event_pattern: str, callback: Callable, 
           priority: EventPriority = EventPriority.NORMAL,
           once: bool = False):
        """
        Register an event handler.
        
        Args:
            event_pattern: Event name or pattern (supports wildcards)
            callback: Function to call when event occurs
            priority: Handler priority
            once: If True, handler is removed after first execution
        """
        with self._lock:
            handler = EventHandler(
                callback=callback,
                event_pattern=event_pattern,
                priority=priority,
                is_async=asyncio.iscoroutinefunction(callback),
                once=once
            )
            
            if event_pattern not in self._handlers:
                self._handlers[event_pattern] = []
            
            # Insert handler sorted by priority
            handlers = self._handlers[event_pattern]
            insert_pos = 0
            for i, h in enumerate(handlers):
                if h.priority.value < handler.priority.value:
                    insert_pos = i
                    break
                insert_pos = i + 1
            
            handlers.insert(insert_pos, handler)
            
            self._logger.debug(f"Registered handler for '{event_pattern}' with priority {priority.name}")
    
    def once(self, event_pattern: str, callback: Callable,
             priority: EventPriority = EventPriority.NORMAL):
        """
        Register a one-time event handler.
        
        Args:
            event_pattern: Event name or pattern
            callback: Function to call when event occurs
            priority: Handler priority
        """
        self.on(event_pattern, callback, priority, once=True)
    
    def off(self, event_pattern: str, callback: Callable):
        """
        Remove an event handler.
        
        Args:
            event_pattern: Event pattern to remove handler from
            callback: Callback function to remove
        """
        with self._lock:
            if event_pattern in self._handlers:
                self._handlers[event_pattern] = [
                    h for h in self._handlers[event_pattern]
                    if h.callback != callback
                ]
                if not self._handlers[event_pattern]:
                    del self._handlers[event_pattern]
    
    def emit(self, event_name: str, data: Dict[str, Any] = None,
             source: str = "system", priority: EventPriority = EventPriority.NORMAL) -> Event:
        """
        Emit an event.
        
        Args:
            event_name: Name of the event
            data: Event data
            source: Source module/component
            priority: Event priority
            
        Returns:
            The emitted Event object
        """
        event = Event(
            name=event_name,
            data=data or {},
            source=source,
            priority=priority,
            event_id=f"{event_name}_{datetime.utcnow().timestamp()}"
        )
        
        # Add to history
        with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
        
        # Find matching handlers
        handlers_to_execute = []
        handlers_to_remove = []
        
        with self._lock:
            for pattern, handlers in self._handlers.items():
                for handler in handlers:
                    if handler.matches(event_name):
                        handlers_to_execute.append(handler)
                        if handler.once:
                            handlers_to_remove.append((pattern, handler))
        
        # Execute handlers
        for handler in sorted(handlers_to_execute, key=lambda h: -h.priority.value):
            try:
                if handler.is_async:
                    # Run async handlers in thread pool
                    self._executor.submit(self._run_async_handler, handler.callback, event)
                else:
                    # Run sync handlers directly
                    handler.callback(event)
            except Exception as e:
                self._logger.error(f"Error in event handler for '{event_name}': {e}")
        
        # Remove one-time handlers
        with self._lock:
            for pattern, handler in handlers_to_remove:
                if pattern in self._handlers and handler in self._handlers[pattern]:
                    self._handlers[pattern].remove(handler)
        
        self._logger.debug(f"Emitted event '{event_name}' from '{source}'")
        return event
    
    def emit_async(self, event_name: str, data: Dict[str, Any] = None,
                   source: str = "system", priority: EventPriority = EventPriority.NORMAL):
        """
        Emit an event asynchronously.
        
        Returns immediately without waiting for handlers to complete.
        """
        self._executor.submit(self.emit, event_name, data, source, priority)
    
    def _run_async_handler(self, callback: Callable, event: Event):
        """Run an async handler in a new event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(callback(event))
        finally:
            loop.close()
    
    def wait_for(self, event_pattern: str, timeout: Optional[float] = None) -> Optional[Event]:
        """
        Wait for an event to occur.
        
        Args:
            event_pattern: Event pattern to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            The event if it occurs, None if timeout
        """
        result = {'event': None}
        event_received = threading.Event()
        
        def handler(event):
            result['event'] = event
            event_received.set()
        
        self.once(event_pattern, handler, EventPriority.CRITICAL)
        
        if event_received.wait(timeout):
            return result['event']
        else:
            self.off(event_pattern, handler)
            return None
    
    def get_handlers(self, event_pattern: Optional[str] = None) -> Dict[str, List[EventHandler]]:
        """
        Get registered handlers.
        
        Args:
            event_pattern: Optional pattern to filter by
            
        Returns:
            Dictionary of handlers
        """
        with self._lock:
            if event_pattern:
                return {event_pattern: self._handlers.get(event_pattern, [])}
            return self._handlers.copy()
    
    def get_event_history(self, event_name: Optional[str] = None,
                         source: Optional[str] = None,
                         limit: int = 100) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_name: Filter by event name
            source: Filter by source
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        with self._lock:
            history = self._event_history.copy()
        
        # Apply filters
        if event_name:
            history = [e for e in history if e.name == event_name]
        if source:
            history = [e for e in history if e.source == source]
        
        # Return most recent events
        return history[-limit:]
    
    def clear_handlers(self, event_pattern: Optional[str] = None):
        """
        Clear event handlers.
        
        Args:
            event_pattern: Pattern to clear handlers for, or None for all
        """
        with self._lock:
            if event_pattern:
                self._handlers.pop(event_pattern, None)
            else:
                self._handlers.clear()
    
    def shutdown(self):
        """Shutdown the event bus and cleanup resources"""
        self._executor.shutdown(wait=True)
        self.clear_handlers()
        self._event_history.clear()


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """
    Get the global event bus instance.
    
    Returns:
        EventBus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus