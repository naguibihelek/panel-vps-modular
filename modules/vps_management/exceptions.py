"""
VPS Management Module Exceptions

Custom exceptions for VPS module operations.
"""


class VPSManagementError(Exception):
    """Base exception for all VPS management errors"""
    pass


class ServerNotFoundError(VPSManagementError):
    """Raised when a server ID doesn't exist"""
    pass


class DomainNotFoundError(VPSManagementError):
    """Raised when a domain doesn't exist"""
    pass


class ConnectionFailureError(VPSManagementError):
    """Raised when server connection fails"""
    pass


class CredentialError(VPSManagementError):
    """Raised when credentials are invalid or missing"""
    pass


class ValidationError(VPSManagementError):
    """Raised when input validation fails"""
    pass


class PermissionError(VPSManagementError):
    """Raised when user lacks required permissions"""
    pass