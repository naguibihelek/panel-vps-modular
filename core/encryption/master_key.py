"""
Master Key Management

This module manages the master encryption key used for all password encryption
in the system. The key is stored securely and loaded once at startup.

CRITICAL: This key must NEVER be exposed outside the Core layer.
"""

import os
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet


class MasterKeyManager:
    """
    Manages the master encryption key for the system.
    
    The master key is loaded from /root/.warmup_master.key and cached in memory.
    This ensures consistent encryption/decryption across all modules.
    """
    
    _instance: Optional['MasterKeyManager'] = None
    _master_key: Optional[bytes] = None
    _fernet: Optional[Fernet] = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the master key manager"""
        if self._master_key is None:
            self._load_master_key()
    
    def _load_master_key(self):
        """
        Load the master key from file.
        
        Raises:
            FileNotFoundError: If master key file doesn't exist
            ValueError: If master key is invalid
        """
        key_path = Path("/root/.warmup_master.key")
        
        if not key_path.exists():
            raise FileNotFoundError(
                f"Master key not found at {key_path}. "
                "The system cannot function without the master encryption key."
            )
        
        try:
            self._master_key = key_path.read_bytes()
            self._fernet = Fernet(self._master_key)
        except Exception as e:
            raise ValueError(f"Invalid master key: {e}")
    
    def get_fernet(self) -> Fernet:
        """
        Get the Fernet instance for encryption/decryption.
        
        Returns:
            Fernet instance
        """
        if self._fernet is None:
            raise RuntimeError("Master key not loaded")
        return self._fernet
    
    def get_key_bytes(self) -> bytes:
        """
        Get the raw master key bytes.
        
        WARNING: Use this only when absolutely necessary.
        Prefer using get_fernet() for encryption operations.
        
        Returns:
            Master key bytes
        """
        if self._master_key is None:
            raise RuntimeError("Master key not loaded")
        return self._master_key
    
    def reload_key(self):
        """
        Reload the master key from file.
        Used for testing or key rotation scenarios.
        """
        self._master_key = None
        self._fernet = None
        self._load_master_key()
    
    @staticmethod
    def generate_new_key() -> bytes:
        """
        Generate a new Fernet key.
        
        This is a utility method for creating new keys.
        It does NOT affect the current master key.
        
        Returns:
            New Fernet key bytes
        """
        return Fernet.generate_key()
    
    def is_loaded(self) -> bool:
        """
        Check if the master key is loaded.
        
        Returns:
            True if master key is loaded, False otherwise
        """
        return self._master_key is not None and self._fernet is not None