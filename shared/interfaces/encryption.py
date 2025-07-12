"""
Encryption Interface

This interface defines how modules interact with the Core encryption service.
Modules MUST use this interface for all encryption/decryption operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class IEncryptionInterface(ABC):
    """
    Encryption interface that all modules must use for encryption operations.
    This prevents direct access to the master key and ensures consistent
    encryption patterns across the system.
    """
    
    @abstractmethod
    def encrypt_password(self, password: str) -> str:
        """Encrypt a password"""
        pass
    
    @abstractmethod
    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt a password"""
        pass
    
    @abstractmethod
    def encrypt_data(self, data: str) -> str:
        """Encrypt generic data"""
        pass
    
    @abstractmethod
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt generic data"""
        pass
    
    @abstractmethod
    def is_encrypted(self, text: str) -> bool:
        """Check if text appears to be encrypted"""
        pass
    
    @abstractmethod
    def verify_encryption_available(self) -> bool:
        """Verify encryption service is available"""
        pass


class EncryptionInterface(IEncryptionInterface):
    """
    Concrete implementation of the encryption interface.
    This is what modules will actually use.
    """
    
    def __init__(self):
        # Import here to avoid circular imports
        from core.encryption import get_encryption_service
        self.service = get_encryption_service()
    
    def encrypt_password(self, password: str) -> str:
        """
        Encrypt a password.
        
        Args:
            password: Plaintext password
            
        Returns:
            Encrypted password string
            
        Raises:
            ValueError: If encryption fails
        """
        if not password:
            raise ValueError("Cannot encrypt empty password")
        return self.service.encrypt(password)
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """
        Decrypt a password.
        
        Args:
            encrypted_password: Encrypted password string
            
        Returns:
            Plaintext password
            
        Raises:
            ValueError: If decryption fails
        """
        if not encrypted_password:
            raise ValueError("Cannot decrypt empty password")
        return self.service.decrypt(encrypted_password)
    
    def encrypt_data(self, data: str) -> str:
        """
        Encrypt generic data.
        
        Args:
            data: Plaintext data
            
        Returns:
            Encrypted data string
            
        Raises:
            ValueError: If encryption fails
        """
        return self.service.encrypt(data)
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt generic data.
        
        Args:
            encrypted_data: Encrypted data string
            
        Returns:
            Plaintext data
            
        Raises:
            ValueError: If decryption fails
        """
        return self.service.decrypt(encrypted_data)
    
    def is_encrypted(self, text: str) -> bool:
        """
        Check if text appears to be encrypted.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be encrypted
        """
        return self.service.is_encrypted(text)
    
    def verify_encryption_available(self) -> bool:
        """
        Verify that the encryption service is available and working.
        
        Returns:
            True if encryption is available
        """
        return self.service.verify_master_key()
    
    def encrypt_batch(self, items: List[str]) -> List[str]:
        """
        Encrypt multiple items efficiently.
        
        Args:
            items: List of plaintext strings
            
        Returns:
            List of encrypted strings
        """
        return self.service.encrypt_batch(items)
    
    def decrypt_batch(self, items: List[str]) -> List[Optional[str]]:
        """
        Decrypt multiple items efficiently.
        
        Args:
            items: List of encrypted strings
            
        Returns:
            List of decrypted strings (None for failed decryptions)
        """
        return self.service.decrypt_batch(items)