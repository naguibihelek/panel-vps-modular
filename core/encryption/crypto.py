"""
Core Encryption Service

This module provides encryption and decryption services for the entire system.
All password encryption/decryption MUST go through this service.
"""

from typing import Optional, Union
from cryptography.fernet import Fernet, InvalidToken
from .master_key import MasterKeyManager


class EncryptionService:
    """
    Centralized encryption service for all modules.
    
    This service ensures consistent encryption/decryption patterns
    and prevents direct access to the master key from modules.
    """
    
    def __init__(self):
        """Initialize the encryption service with the master key"""
        self.key_manager = MasterKeyManager()
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Base64-encoded encrypted string
            
        Raises:
            ValueError: If plaintext is empty or invalid
        """
        if not plaintext:
            raise ValueError("Cannot encrypt empty string")
        
        try:
            fernet = self.key_manager.get_fernet()
            encrypted_bytes = fernet.encrypt(plaintext.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Encryption failed: {e}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            ciphertext: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
            
        Raises:
            ValueError: If decryption fails or ciphertext is invalid
        """
        if not ciphertext:
            raise ValueError("Cannot decrypt empty string")
        
        try:
            fernet = self.key_manager.get_fernet()
            
            # Handle both string and bytes input
            if isinstance(ciphertext, str):
                ciphertext_bytes = ciphertext.encode('utf-8')
            else:
                ciphertext_bytes = ciphertext
            
            decrypted_bytes = fernet.decrypt(ciphertext_bytes)
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            raise ValueError("Invalid ciphertext or wrong key")
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    def encrypt_batch(self, plaintexts: list[str]) -> list[str]:
        """
        Encrypt multiple strings efficiently.
        
        Args:
            plaintexts: List of strings to encrypt
            
        Returns:
            List of encrypted strings
        """
        return [self.encrypt(text) for text in plaintexts if text]
    
    def decrypt_batch(self, ciphertexts: list[str]) -> list[str]:
        """
        Decrypt multiple strings efficiently.
        
        Args:
            ciphertexts: List of encrypted strings
            
        Returns:
            List of decrypted strings
        """
        results = []
        for ciphertext in ciphertexts:
            try:
                results.append(self.decrypt(ciphertext))
            except ValueError:
                # Return None for failed decryptions
                results.append(None)
        return results
    
    def is_encrypted(self, text: str) -> bool:
        """
        Check if a string appears to be encrypted.
        
        This is a heuristic check based on Fernet format.
        
        Args:
            text: String to check
            
        Returns:
            True if string appears to be encrypted
        """
        if not text:
            return False
        
        try:
            # Fernet tokens are base64-encoded and have specific format
            # Try to decrypt - if it works, it's encrypted
            self.decrypt(text)
            return True
        except:
            return False
    
    def generate_key(self) -> str:
        """
        Generate a new encryption key.
        
        This is useful for creating new keys for specific purposes.
        Does NOT affect the master key.
        
        Returns:
            New Fernet key as string
        """
        return Fernet.generate_key().decode('utf-8')
    
    def verify_master_key(self) -> bool:
        """
        Verify that the master key is loaded and valid.
        
        Returns:
            True if master key is valid
        """
        return self.key_manager.is_loaded()


# Global instance for convenience
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get the global encryption service instance.
    
    Returns:
        EncryptionService instance
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service