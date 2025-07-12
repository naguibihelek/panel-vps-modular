"""
Core Foundation Layer

This layer provides essential services that all modules depend on.
It is STABLE and should not be modified without careful consideration.

Services provided:
- Database access and connection management
- Encryption services for passwords and sensitive data
- Authentication and session management
- Common utilities and logging
"""

from .database import (
    DatabaseService,
    get_db,
    Base,
    BaseModel,
    TimestampMixin,
    DatabaseQueries,
    QueryBuilder
)

from .encryption import (
    EncryptionService,
    get_encryption_service
)

from .auth import (
    AuthenticationService,
    get_auth_service,
    SessionManager,
    get_session_manager,
    APIKeyManager,
    get_api_key_manager
)

from .utils import (
    EventBus,
    get_event_bus,
    get_logger,
    get_module_logger,
    get_error_handler,
    BaseSystemError
)

__all__ = [
    # Database
    'DatabaseService',
    'get_db',
    'Base',
    'BaseModel',
    'TimestampMixin',
    'DatabaseQueries',
    'QueryBuilder',
    
    # Encryption
    'EncryptionService',
    'get_encryption_service',
    
    # Authentication
    'AuthenticationService',
    'get_auth_service',
    'SessionManager',
    'get_session_manager',
    'APIKeyManager',
    'get_api_key_manager',
    
    # Utils
    'EventBus',
    'get_event_bus',
    'get_logger',
    'get_module_logger',
    'get_error_handler',
    'BaseSystemError'
]