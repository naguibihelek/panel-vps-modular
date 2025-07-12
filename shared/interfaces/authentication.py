"""
Authentication Interface

This interface defines how modules interact with the Core authentication service.
Modules MUST use this interface for all authentication operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class IAuthenticationInterface(ABC):
    """
    Authentication interface that all modules must use for auth operations.
    This ensures consistent authentication patterns across the system.
    """
    
    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate a user and return session ID"""
        pass
    
    @abstractmethod
    def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Verify a session and return user info"""
        pass
    
    @abstractmethod
    def logout_session(self, session_id: str) -> bool:
        """Logout a session"""
        pass
    
    @abstractmethod
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify an API key and return user info"""
        pass
    
    @abstractmethod
    def check_permission(self, session_id: str, permission: str) -> bool:
        """Check if a session has a specific permission"""
        pass
    
    @abstractmethod
    def is_admin(self, session_id: str) -> bool:
        """Check if a session belongs to an admin"""
        pass


class AuthenticationInterface(IAuthenticationInterface):
    """
    Concrete implementation of the authentication interface.
    This is what modules will actually use.
    """
    
    def __init__(self):
        # Import here to avoid circular imports
        from core.auth import get_auth_service, get_api_key_manager
        self.auth_service = get_auth_service()
        self.api_key_manager = get_api_key_manager()
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Session ID if successful, None otherwise
        """
        return self.auth_service.authenticate(username, password)
    
    def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Verify a session and return user information.
        
        Args:
            session_id: Session ID to verify
            
        Returns:
            User info dict if valid, None otherwise
        """
        return self.auth_service.verify_session(session_id)
    
    def logout_session(self, session_id: str) -> bool:
        """
        Logout a session.
        
        Args:
            session_id: Session ID to logout
            
        Returns:
            True if successful
        """
        return self.auth_service.logout(session_id)
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Verify an API key and return user information.
        
        Args:
            api_key: API key to verify
            
        Returns:
            User info dict if valid, None otherwise
        """
        key_obj = self.api_key_manager.verify_api_key(api_key)
        if not key_obj:
            return None
        
        return {
            "username": key_obj.username,
            "key_name": key_obj.name,
            "permissions": key_obj.permissions,
            "is_admin": "*" in key_obj.permissions
        }
    
    def check_permission(self, session_id: str, permission: str) -> bool:
        """
        Check if a session has a specific permission.
        
        Args:
            session_id: Session ID to check
            permission: Permission to verify
            
        Returns:
            True if session has permission
        """
        user_info = self.verify_session(session_id)
        if not user_info:
            return False
        
        # Admins have all permissions
        if user_info.get("is_admin"):
            return True
        
        # In the future, implement granular permissions
        return False
    
    def is_admin(self, session_id: str) -> bool:
        """
        Check if a session belongs to an admin user.
        
        Args:
            session_id: Session ID to check
            
        Returns:
            True if admin session
        """
        user_info = self.verify_session(session_id)
        return user_info.get("is_admin", False) if user_info else False
    
    def create_api_key(self, username: str, key_name: str, 
                      permissions: List[str] = None) -> Optional[tuple[str, str]]:
        """
        Create a new API key for a user.
        
        Args:
            username: Username to create key for
            key_name: Descriptive name for the key
            permissions: List of permissions
            
        Returns:
            Tuple of (key_id, api_key) if successful
        """
        return self.api_key_manager.create_api_key(
            username=username,
            name=key_name,
            permissions=permissions or ["read"]
        )
    
    def revoke_api_key(self, key_id: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_id: Key ID to revoke
            
        Returns:
            True if successful
        """
        return self.api_key_manager.revoke_api_key(key_id)
    
    def change_password(self, username: str, old_password: str, 
                       new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            username: Username whose password to change
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful
        """
        return self.auth_service.change_password(username, old_password, new_password)