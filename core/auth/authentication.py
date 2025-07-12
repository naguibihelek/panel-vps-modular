"""
Core Authentication Service

This module provides authentication services for the entire system.
It handles user authentication, password verification, and session management.
"""

import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime
from .session import SessionManager, get_session_manager


class AuthenticationService:
    """
    Centralized authentication service for all modules.
    
    Currently uses hardcoded credentials for backward compatibility.
    Future versions will support database-backed user management.
    """
    
    # Default admin credentials (for backward compatibility)
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "StrongPass123"
    
    def __init__(self):
        """Initialize the authentication service"""
        self.session_manager = get_session_manager()
        
        # In-memory user store (will be replaced with database)
        self._users = {
            self.DEFAULT_ADMIN_USERNAME: {
                "username": self.DEFAULT_ADMIN_USERNAME,
                "password_hash": self._hash_password(self.DEFAULT_ADMIN_PASSWORD),
                "is_admin": True,
                "created_at": datetime.utcnow()
            }
        }
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Session ID if authentication successful, None otherwise
        """
        user = self._users.get(username)
        if not user:
            return None
        
        if not self._verify_password(password, user["password_hash"]):
            return None
        
        # Create session
        session_data = {
            "is_admin": user.get("is_admin", False),
            "login_time": datetime.utcnow().isoformat()
        }
        
        session_id = self.session_manager.create_session(username, session_data)
        return session_id
    
    def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Verify a session and return user information.
        
        Args:
            session_id: Session ID to verify
            
        Returns:
            User information dict if session valid, None otherwise
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            return None
        
        user = self._users.get(session.username)
        if not user:
            return None
        
        return {
            "username": session.username,
            "is_admin": session.data.get("is_admin", False),
            "session_created": session.created_at,
            "last_activity": session.last_activity
        }
    
    def logout(self, session_id: str) -> bool:
        """
        Logout a user by destroying their session.
        
        Args:
            session_id: Session ID to logout
            
        Returns:
            True if logout successful
        """
        self.session_manager.destroy_session(session_id)
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            username: Username whose password to change
            old_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if password changed successfully
        """
        user = self._users.get(username)
        if not user:
            return False
        
        if not self._verify_password(old_password, user["password_hash"]):
            return False
        
        user["password_hash"] = self._hash_password(new_password)
        
        # Invalidate all existing sessions for this user
        self.session_manager.destroy_user_sessions(username)
        
        return True
    
    def create_api_key(self, username: str) -> Optional[str]:
        """
        Create an API key for a user.
        
        Args:
            username: Username to create API key for
            
        Returns:
            API key if successful, None otherwise
        """
        user = self._users.get(username)
        if not user:
            return None
        
        api_key = secrets.token_urlsafe(32)
        user["api_key"] = self._hash_password(api_key)
        user["api_key_created"] = datetime.utcnow()
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """
        Verify an API key and return the username.
        
        Args:
            api_key: API key to verify
            
        Returns:
            Username if API key valid, None otherwise
        """
        for username, user in self._users.items():
            if "api_key" in user:
                if self._verify_password(api_key, user["api_key"]):
                    return username
        return None
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA256.
        
        In production, this should use bcrypt or argon2.
        
        Args:
            password: Password to hash
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Password to verify
            password_hash: Hash to verify against
            
        Returns:
            True if password matches
        """
        return self._hash_password(password) == password_hash
    
    def get_active_sessions_count(self) -> int:
        """Get the number of active sessions"""
        return self.session_manager.session_count()
    
    def is_admin(self, username: str) -> bool:
        """
        Check if a user is an admin.
        
        Args:
            username: Username to check
            
        Returns:
            True if user is admin
        """
        user = self._users.get(username)
        return user.get("is_admin", False) if user else False


# Global authentication service instance
_auth_service: Optional[AuthenticationService] = None


def get_auth_service() -> AuthenticationService:
    """
    Get the global authentication service instance.
    
    Returns:
        AuthenticationService instance
    """
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthenticationService()
    return _auth_service