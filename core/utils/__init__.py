"""
Core Utilities Module

This module provides common utilities used throughout the system.
"""

from .event_bus import (
    EventBus,
    Event,
    EventPriority,
    EventHandler,
    get_event_bus
)

from .logging import (
    LoggingService,
    ModuleLogger,
    get_logging_service,
    get_logger,
    get_module_logger
)

from .errors import (
    BaseSystemError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    DatabaseError,
    ModuleBoundaryError,
    ConfigurationError,
    ServiceUnavailableError,
    ResourceNotFoundError,
    RateLimitError,
    ErrorHandler,
    get_error_handler
)

__all__ = [
    # Event Bus
    'EventBus',
    'Event',
    'EventPriority',
    'EventHandler',
    'get_event_bus',
    
    # Logging
    'LoggingService',
    'ModuleLogger',
    'get_logging_service',
    'get_logger',
    'get_module_logger',
    
    # Errors
    'BaseSystemError',
    'AuthenticationError',
    'AuthorizationError',
    'ValidationError',
    'DatabaseError',
    'ModuleBoundaryError',
    'ConfigurationError',
    'ServiceUnavailableError',
    'ResourceNotFoundError',
    'RateLimitError',
    'ErrorHandler',
    'get_error_handler'
]