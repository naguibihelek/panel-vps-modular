"""
System-wide Error Handling

This module provides centralized error handling and custom exception
classes for the entire system.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import traceback
import logging


class BaseSystemError(Exception):
    """
    Base exception class for all system errors.
    """
    
    def __init__(self, message: str, code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize system error.
        
        Args:
            message: Error message
            code: Error code for categorization
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization"""
        return {
            'error': self.code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class AuthenticationError(BaseSystemError):
    """Raised when authentication fails"""
    pass


class AuthorizationError(BaseSystemError):
    """Raised when authorization fails"""
    pass


class ValidationError(BaseSystemError):
    """Raised when data validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None,
                 validation_errors: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            validation_errors: List of validation errors
        """
        details = {}
        if field:
            details['field'] = field
        if validation_errors:
            details['validation_errors'] = validation_errors
        
        super().__init__(message, 'VALIDATION_ERROR', details)


class DatabaseError(BaseSystemError):
    """Raised when database operations fail"""
    pass


class ModuleBoundaryError(BaseSystemError):
    """Raised when module boundaries are violated"""
    
    def __init__(self, source_module: str, target_module: str, operation: str):
        """
        Initialize module boundary error.
        
        Args:
            source_module: Module attempting the operation
            target_module: Module being accessed
            operation: Operation being attempted
        """
        message = f"Module '{source_module}' cannot {operation} module '{target_module}'"
        details = {
            'source_module': source_module,
            'target_module': target_module,
            'operation': operation
        }
        super().__init__(message, 'MODULE_BOUNDARY_VIOLATION', details)


class ConfigurationError(BaseSystemError):
    """Raised when configuration is invalid or missing"""
    pass


class ServiceUnavailableError(BaseSystemError):
    """Raised when a required service is unavailable"""
    
    def __init__(self, service_name: str, reason: Optional[str] = None):
        """
        Initialize service unavailable error.
        
        Args:
            service_name: Name of the unavailable service
            reason: Reason for unavailability
        """
        message = f"Service '{service_name}' is unavailable"
        if reason:
            message += f": {reason}"
        
        details = {'service': service_name}
        if reason:
            details['reason'] = reason
        
        super().__init__(message, 'SERVICE_UNAVAILABLE', details)


class ResourceNotFoundError(BaseSystemError):
    """Raised when a requested resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: Any):
        """
        Initialize resource not found error.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the missing resource
        """
        message = f"{resource_type} with ID '{resource_id}' not found"
        details = {
            'resource_type': resource_type,
            'resource_id': str(resource_id)
        }
        super().__init__(message, 'RESOURCE_NOT_FOUND', details)


class RateLimitError(BaseSystemError):
    """Raised when rate limits are exceeded"""
    
    def __init__(self, limit: int, window: str, retry_after: Optional[int] = None):
        """
        Initialize rate limit error.
        
        Args:
            limit: Rate limit that was exceeded
            window: Time window for the limit
            retry_after: Seconds until retry is allowed
        """
        message = f"Rate limit exceeded: {limit} requests per {window}"
        details = {
            'limit': limit,
            'window': window
        }
        if retry_after:
            details['retry_after'] = retry_after
        
        super().__init__(message, 'RATE_LIMIT_EXCEEDED', details)


class ErrorHandler:
    """
    Central error handling service.
    """
    
    def __init__(self):
        """Initialize error handler"""
        self.logger = logging.getLogger(__name__)
        self._error_callbacks = []
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle an error and return standardized error response.
        
        Args:
            error: The exception to handle
            context: Additional context about where the error occurred
            
        Returns:
            Standardized error dictionary
        """
        # Log the error
        self._log_error(error, context)
        
        # Execute callbacks
        for callback in self._error_callbacks:
            try:
                callback(error, context)
            except Exception as cb_error:
                self.logger.error(f"Error in error callback: {cb_error}")
        
        # Create error response
        if isinstance(error, BaseSystemError):
            return error.to_dict()
        else:
            # Handle non-system errors
            return {
                'error': 'INTERNAL_ERROR',
                'message': 'An internal error occurred',
                'details': {
                    'type': type(error).__name__,
                    'original_message': str(error)
                },
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context"""
        if isinstance(error, BaseSystemError):
            log_data = {
                'error_code': error.code,
                'error_message': error.message,
                'error_details': error.details
            }
        else:
            log_data = {
                'error_type': type(error).__name__,
                'error_message': str(error)
            }
        
        if context:
            log_data['context'] = context
        
        # Add stack trace for non-system errors
        if not isinstance(error, BaseSystemError):
            log_data['traceback'] = traceback.format_exc()
        
        self.logger.error(
            f"Error occurred: {error}",
            extra={'extra_data': log_data}
        )
    
    def register_error_callback(self, callback: callable):
        """
        Register a callback to be executed when errors occur.
        
        Args:
            callback: Function to call with (error, context) arguments
        """
        self._error_callbacks.append(callback)
    
    def create_error_response(self, status_code: int, error: Exception) -> Dict[str, Any]:
        """
        Create an HTTP error response.
        
        Args:
            status_code: HTTP status code
            error: The error that occurred
            
        Returns:
            Error response dictionary
        """
        error_data = self.handle_error(error)
        return {
            'status_code': status_code,
            'error': error_data
        }


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """
    Get the global error handler instance.
    
    Returns:
        ErrorHandler instance
    """
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler