"""
Base Module Interface

This defines the standard interface that all modules must implement.
It ensures consistent module initialization, communication, and lifecycle management.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ModuleInfo:
    """Information about a module"""
    name: str
    version: str
    description: str
    dependencies: List[str]
    provides: List[str]  # Services/interfaces this module provides
    consumes: List[str]  # Services/interfaces this module consumes
    status: str = "inactive"
    initialized_at: Optional[datetime] = None


class IModule(ABC):
    """
    Base interface that all modules must implement.
    """
    
    @abstractmethod
    def get_info(self) -> ModuleInfo:
        """Get module information"""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the module with configuration.
        
        Args:
            config: Module-specific configuration
            
        Returns:
            True if initialization successful
        """
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """
        Start the module (after initialization).
        
        Returns:
            True if started successfully
        """
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """
        Stop the module gracefully.
        
        Returns:
            True if stopped successfully
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the module.
        
        Returns:
            Health status dictionary with at least:
            - healthy: bool
            - message: str
            - details: dict (optional)
        """
        pass
    
    @abstractmethod
    def get_interface(self) -> Any:
        """
        Get the public interface for this module.
        
        Returns:
            The module's public interface object
        """
        pass
    
    @abstractmethod
    def handle_event(self, event_name: str, event_data: Dict[str, Any]):
        """
        Handle an incoming event.
        
        Args:
            event_name: Name of the event
            event_data: Event data
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get module statistics.
        
        Returns:
            Statistics dictionary
        """
        pass


class BaseModule(IModule):
    """
    Base implementation of IModule that modules can extend.
    Provides common functionality for all modules.
    """
    
    def __init__(self, name: str, version: str, description: str):
        """
        Initialize base module.
        
        Args:
            name: Module name
            version: Module version
            description: Module description
        """
        self.name = name
        self.version = version
        self.description = description
        self.config = {}
        self.is_initialized = False
        self.is_running = False
        self.initialized_at = None
        
        # Import Core services
        from core import get_logger, get_event_bus, get_error_handler
        from shared.interfaces import DatabaseInterface, EncryptionInterface, AuthenticationInterface
        
        # Core services
        self.logger = get_logger(f"module.{name}")
        self.event_bus = get_event_bus()
        self.error_handler = get_error_handler()
        
        # Interfaces
        self.db = DatabaseInterface()
        self.encryption = EncryptionInterface()
        self.auth = AuthenticationInterface()
        
    def get_info(self) -> ModuleInfo:
        """Get module information"""
        return ModuleInfo(
            name=self.name,
            version=self.version,
            description=self.description,
            dependencies=self._get_dependencies(),
            provides=self._get_provides(),
            consumes=self._get_consumes(),
            status="running" if self.is_running else "initialized" if self.is_initialized else "inactive",
            initialized_at=self.initialized_at
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the module"""
        try:
            self.logger.info(f"Initializing module {self.name}")
            self.config = config
            
            # Call module-specific initialization
            if self._initialize():
                self.is_initialized = True
                self.initialized_at = datetime.utcnow()
                
                # Emit initialization event
                self.event_bus.emit(
                    "system.module_initialized",
                    {"module": self.name, "version": self.version},
                    source=self.name
                )
                
                self.logger.info(f"Module {self.name} initialized successfully")
                return True
            else:
                self.logger.error(f"Module {self.name} initialization failed")
                return False
                
        except Exception as e:
            self.error_handler.handle_error(e, {"module": self.name, "phase": "initialization"})
            return False
    
    def start(self) -> bool:
        """Start the module"""
        if not self.is_initialized:
            self.logger.error(f"Cannot start module {self.name}: not initialized")
            return False
        
        try:
            self.logger.info(f"Starting module {self.name}")
            
            # Register event handlers
            self._register_event_handlers()
            
            # Call module-specific start
            if self._start():
                self.is_running = True
                
                # Emit start event
                self.event_bus.emit(
                    "system.module_started",
                    {"module": self.name},
                    source=self.name
                )
                
                self.logger.info(f"Module {self.name} started successfully")
                return True
            else:
                self.logger.error(f"Module {self.name} start failed")
                return False
                
        except Exception as e:
            self.error_handler.handle_error(e, {"module": self.name, "phase": "start"})
            return False
    
    def stop(self) -> bool:
        """Stop the module"""
        if not self.is_running:
            return True
        
        try:
            self.logger.info(f"Stopping module {self.name}")
            
            # Call module-specific stop
            if self._stop():
                self.is_running = False
                
                # Unregister event handlers
                self._unregister_event_handlers()
                
                # Emit stop event
                self.event_bus.emit(
                    "system.module_stopped",
                    {"module": self.name},
                    source=self.name
                )
                
                self.logger.info(f"Module {self.name} stopped successfully")
                return True
            else:
                self.logger.error(f"Module {self.name} stop failed")
                return False
                
        except Exception as e:
            self.error_handler.handle_error(e, {"module": self.name, "phase": "stop"})
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        base_health = {
            "healthy": self.is_initialized and self.is_running,
            "message": f"Module {self.name} is {'running' if self.is_running else 'not running'}",
            "details": {
                "initialized": self.is_initialized,
                "running": self.is_running,
                "uptime": (datetime.utcnow() - self.initialized_at).total_seconds() if self.initialized_at else 0
            }
        }
        
        # Get module-specific health
        try:
            module_health = self._health_check()
            if module_health:
                base_health["details"].update(module_health)
        except Exception as e:
            base_health["healthy"] = False
            base_health["message"] = f"Health check failed: {str(e)}"
        
        return base_health
    
    def handle_event(self, event_name: str, event_data: Dict[str, Any]):
        """Handle incoming event"""
        # This will be called by event handlers registered in _register_event_handlers
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get module statistics"""
        base_stats = {
            "module": self.name,
            "version": self.version,
            "status": self.get_info().status,
            "uptime_seconds": (datetime.utcnow() - self.initialized_at).total_seconds() if self.initialized_at else 0
        }
        
        # Get module-specific stats
        try:
            module_stats = self._get_stats()
            if module_stats:
                base_stats.update(module_stats)
        except Exception as e:
            self.logger.error(f"Failed to get module stats: {e}")
        
        return base_stats
    
    # Abstract methods that modules must implement
    
    @abstractmethod
    def _get_dependencies(self) -> List[str]:
        """Get list of module dependencies"""
        pass
    
    @abstractmethod
    def _get_provides(self) -> List[str]:
        """Get list of services this module provides"""
        pass
    
    @abstractmethod
    def _get_consumes(self) -> List[str]:
        """Get list of services this module consumes"""
        pass
    
    @abstractmethod
    def _initialize(self) -> bool:
        """Module-specific initialization"""
        pass
    
    @abstractmethod
    def _start(self) -> bool:
        """Module-specific start logic"""
        pass
    
    @abstractmethod
    def _stop(self) -> bool:
        """Module-specific stop logic"""
        pass
    
    @abstractmethod
    def _health_check(self) -> Dict[str, Any]:
        """Module-specific health check"""
        pass
    
    @abstractmethod
    def _get_stats(self) -> Dict[str, Any]:
        """Module-specific statistics"""
        pass
    
    @abstractmethod
    def _register_event_handlers(self):
        """Register module event handlers"""
        pass
    
    @abstractmethod
    def _unregister_event_handlers(self):
        """Unregister module event handlers"""
        pass
    
    @abstractmethod
    def get_interface(self) -> Any:
        """Get the public interface for this module"""
        pass