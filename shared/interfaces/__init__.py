"""
Shared Interfaces Module

This module contains all the interfaces that modules use to communicate
with each other and with the Core Foundation layer.
"""

from .database import DatabaseInterface, IDatabaseInterface
from .encryption import EncryptionInterface, IEncryptionInterface
from .authentication import AuthenticationInterface, IAuthenticationInterface
from .base_module import IModule, BaseModule, ModuleInfo
from .module_registry import ModuleRegistry, get_module_registry

__all__ = [
    # Core Interfaces
    'DatabaseInterface',
    'IDatabaseInterface',
    'EncryptionInterface',
    'IEncryptionInterface',
    'AuthenticationInterface',
    'IAuthenticationInterface',
    
    # Module System
    'IModule',
    'BaseModule',
    'ModuleInfo',
    'ModuleRegistry',
    'get_module_registry'
]