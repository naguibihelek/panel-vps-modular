"""
Core Encryption Module

This module provides centralized encryption services for the entire system.
All password encryption/decryption operations MUST go through this module.

CRITICAL: The master key must NEVER leave this module.
"""

from .crypto import (
    EncryptionService,
    get_encryption_service
)
from .master_key import MasterKeyManager

__all__ = [
    'EncryptionService',
    'get_encryption_service',
    'MasterKeyManager'
]