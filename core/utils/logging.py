"""
System-wide Logging Configuration

This module provides centralized logging configuration and utilities
for the entire system.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional, Dict, Any
import json


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs for better parsing.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'thread': record.thread,
            'thread_name': record.threadName
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class ModuleLogger:
    """
    Logger wrapper that adds module context to all log messages.
    """
    
    def __init__(self, module_name: str, logger: logging.Logger):
        """
        Initialize module logger.
        
        Args:
            module_name: Name of the module
            logger: Underlying logger instance
        """
        self.module_name = module_name
        self.logger = logger
    
    def _log(self, level: int, msg: str, extra_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Internal log method that adds module context"""
        extra = kwargs.get('extra', {})
        extra['module_name'] = self.module_name
        if extra_data:
            extra['extra_data'] = extra_data
        kwargs['extra'] = extra
        self.logger.log(level, msg, **kwargs)
    
    def debug(self, msg: str, extra_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, msg, extra_data, **kwargs)
    
    def info(self, msg: str, extra_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message"""
        self._log(logging.INFO, msg, extra_data, **kwargs)
    
    def warning(self, msg: str, extra_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message"""
        self._log(logging.WARNING, msg, extra_data, **kwargs)
    
    def error(self, msg: str, extra_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log error message"""
        self._log(logging.ERROR, msg, extra_data, **kwargs)
    
    def critical(self, msg: str, extra_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log critical message"""
        self._log(logging.CRITICAL, msg, extra_data, **kwargs)


class LoggingService:
    """
    Central logging service for the system.
    """
    
    def __init__(self):
        """Initialize the logging service"""
        self._loggers: Dict[str, logging.Logger] = {}
        self._configured = False
        self._log_dir = "/var/log/panel"
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        if not os.path.exists(self._log_dir):
            try:
                os.makedirs(self._log_dir, exist_ok=True)
            except:
                # Fall back to local directory if /var/log is not writable
                self._log_dir = "./logs"
                os.makedirs(self._log_dir, exist_ok=True)
    
    def configure(self, 
                  level: str = "INFO",
                  enable_console: bool = True,
                  enable_file: bool = True,
                  structured: bool = False):
        """
        Configure the logging system.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_console: Enable console output
            enable_file: Enable file output
            structured: Use structured JSON logging
        """
        if self._configured:
            return
        
        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        if structured:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if enable_file:
            file_handler = logging.handlers.RotatingFileHandler(
                os.path.join(self._log_dir, 'panel.log'),
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
            # Error file handler
            error_handler = logging.handlers.RotatingFileHandler(
                os.path.join(self._log_dir, 'panel_errors.log'),
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            root_logger.addHandler(error_handler)
        
        self._configured = True
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance.
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Logger instance
        """
        if not self._configured:
            self.configure()
        
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        
        return self._loggers[name]
    
    def get_module_logger(self, module_name: str) -> ModuleLogger:
        """
        Get a module-specific logger.
        
        Args:
            module_name: Name of the module
            
        Returns:
            ModuleLogger instance
        """
        logger = self.get_logger(f"module.{module_name}")
        return ModuleLogger(module_name, logger)
    
    def log_event(self, event_name: str, event_data: Dict[str, Any], 
                  source: str = "system"):
        """
        Log an event to the event log.
        
        Args:
            event_name: Name of the event
            event_data: Event data
            source: Event source
        """
        event_logger = self.get_logger("events")
        event_logger.info(
            f"Event: {event_name}",
            extra={
                'extra_data': {
                    'event_name': event_name,
                    'source': source,
                    'data': event_data
                }
            }
        )
    
    def log_api_request(self, method: str, path: str, 
                       status_code: int, duration_ms: float,
                       user: Optional[str] = None):
        """
        Log an API request.
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            user: Username if authenticated
        """
        api_logger = self.get_logger("api")
        api_logger.info(
            f"{method} {path} - {status_code} ({duration_ms:.2f}ms)",
            extra={
                'extra_data': {
                    'method': method,
                    'path': path,
                    'status_code': status_code,
                    'duration_ms': duration_ms,
                    'user': user
                }
            }
        )
    
    def set_log_level(self, logger_name: str, level: str):
        """
        Set log level for a specific logger.
        
        Args:
            logger_name: Logger name
            level: New log level
        """
        logger = self.get_logger(logger_name)
        logger.setLevel(getattr(logging, level.upper()))


# Global logging service instance
_logging_service: Optional[LoggingService] = None


def get_logging_service() -> LoggingService:
    """
    Get the global logging service instance.
    
    Returns:
        LoggingService instance
    """
    global _logging_service
    if _logging_service is None:
        _logging_service = LoggingService()
    return _logging_service


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return get_logging_service().get_logger(name)


def get_module_logger(module_name: str) -> ModuleLogger:
    """
    Convenience function to get a module logger.
    
    Args:
        module_name: Module name
        
    Returns:
        ModuleLogger instance
    """
    return get_logging_service().get_module_logger(module_name)