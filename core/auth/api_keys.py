"""
API Key Management

This module handles API key creation, validation, and management
for programmatic access to the system.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class APIKey:
    """Represents an API key"""
    key_id: str
    key_hash: str
    username: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    permissions: List[str]
    is_active: bool = True
    
    def is_expired(self) -> bool:
        """Check if the API key has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def has_permission(self, permission: str) -> bool:
        """Check if the API key has a specific permission"""
        return permission in self.permissions or "*" in self.permissions


class APIKeyManager:
    """
    Manages API keys for the authentication system.
    
    API keys provide an alternative authentication method for
    programmatic access to the system.
    """
    
    def __init__(self):
        """Initialize the API key manager"""
        # In-memory storage (should be database-backed in production)
        self._keys: Dict[str, APIKey] = {}
        
    def create_api_key(self, username: str, name: str, 
                      permissions: List[str] = None,
                      expires_in_days: Optional[int] = None) -> tuple[str, str]:
        """
        Create a new API key.
        
        Args:
            username: Username who owns the key
            name: Descriptive name for the key
            permissions: List of permissions for the key
            expires_in_days: Number of days until expiration (None = never)
            
        Returns:
            Tuple of (key_id, api_key)
        """
        # Generate secure random key
        api_key = f"pk_{secrets.token_urlsafe(32)}"
        key_id = secrets.token_hex(8)
        
        # Hash the key for storage
        key_hash = self._hash_key(api_key)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create key object
        key_obj = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            username=username,
            name=name,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_used=None,
            permissions=permissions or ["read"],
            is_active=True
        )
        
        self._keys[key_id] = key_obj
        
        return key_id, api_key
    
    def verify_api_key(self, api_key: str) -> Optional[APIKey]:
        """
        Verify an API key and return its information.
        
        Args:
            api_key: API key to verify
            
        Returns:
            APIKey object if valid, None otherwise
        """
        key_hash = self._hash_key(api_key)
        
        for key_obj in self._keys.values():
            if not key_obj.is_active:
                continue
                
            if key_obj.is_expired():
                continue
                
            if key_obj.key_hash == key_hash:
                # Update last used timestamp
                key_obj.last_used = datetime.utcnow()
                return key_obj
        
        return None
    
    def revoke_api_key(self, key_id: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_id: Key ID to revoke
            
        Returns:
            True if revoked successfully
        """
        if key_id in self._keys:
            self._keys[key_id].is_active = False
            return True
        return False
    
    def list_user_keys(self, username: str) -> List[Dict[str, Any]]:
        """
        List all API keys for a user.
        
        Args:
            username: Username to list keys for
            
        Returns:
            List of key information (without the actual keys)
        """
        user_keys = []
        
        for key_obj in self._keys.values():
            if key_obj.username == username:
                user_keys.append({
                    "key_id": key_obj.key_id,
                    "name": key_obj.name,
                    "created_at": key_obj.created_at,
                    "expires_at": key_obj.expires_at,
                    "last_used": key_obj.last_used,
                    "permissions": key_obj.permissions,
                    "is_active": key_obj.is_active,
                    "is_expired": key_obj.is_expired()
                })
        
        return user_keys
    
    def rotate_api_key(self, key_id: str) -> Optional[str]:
        """
        Rotate an API key (revoke old, create new with same permissions).
        
        Args:
            key_id: Key ID to rotate
            
        Returns:
            New API key if successful, None otherwise
        """
        old_key = self._keys.get(key_id)
        if not old_key or not old_key.is_active:
            return None
        
        # Revoke old key
        old_key.is_active = False
        
        # Create new key with same settings
        expires_in_days = None
        if old_key.expires_at:
            remaining_days = (old_key.expires_at - datetime.utcnow()).days
            expires_in_days = max(1, remaining_days)
        
        new_key_id, new_api_key = self.create_api_key(
            username=old_key.username,
            name=f"{old_key.name} (rotated)",
            permissions=old_key.permissions,
            expires_in_days=expires_in_days
        )
        
        return new_api_key
    
    def check_permission(self, api_key: str, permission: str) -> bool:
        """
        Check if an API key has a specific permission.
        
        Args:
            api_key: API key to check
            permission: Permission to verify
            
        Returns:
            True if key has permission
        """
        key_obj = self.verify_api_key(api_key)
        if not key_obj:
            return False
        
        return key_obj.has_permission(permission)
    
    def _hash_key(self, api_key: str) -> str:
        """Hash an API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def cleanup_expired_keys(self):
        """Remove expired keys from storage"""
        expired_keys = [
            key_id for key_id, key_obj in self._keys.items()
            if key_obj.is_expired()
        ]
        
        for key_id in expired_keys:
            del self._keys[key_id]
    
    def get_key_count(self) -> Dict[str, int]:
        """Get statistics about API keys"""
        total = len(self._keys)
        active = sum(1 for k in self._keys.values() if k.is_active)
        expired = sum(1 for k in self._keys.values() if k.is_expired())
        
        return {
            "total": total,
            "active": active,
            "expired": expired,
            "revoked": total - active - expired
        }


# Global API key manager instance
_api_key_manager: Optional[APIKeyManager] = None


def get_api_key_manager() -> APIKeyManager:
    """
    Get the global API key manager instance.
    
    Returns:
        APIKeyManager instance
    """
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager