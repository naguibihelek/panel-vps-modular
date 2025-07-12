"""
VPS Management Module

Manages mail server infrastructure, domains, and DNS settings.
"""

from .module import VPSModule, get_module
from .interface import VPSManagementInterface, ServerConnection
from .exceptions import (
    VPSManagementError,
    ServerNotFoundError,
    DomainNotFoundError,
    ConnectionFailureError,
    CredentialError,
    ValidationError,
    PermissionError
)

__all__ = [
    'VPSModule',
    'get_module',
    'VPSManagementInterface',
    'ServerConnection',
    'VPSManagementError',
    'ServerNotFoundError',
    'DomainNotFoundError',
    'ConnectionFailureError',
    'CredentialError',
    'ValidationError',
    'PermissionError'
]