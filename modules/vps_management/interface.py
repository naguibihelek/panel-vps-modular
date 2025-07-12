"""
VPS Management Module Interface

This module provides the public interface for VPS server and domain management.
Other modules should only interact with VPS functionality through this interface.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ServerConnection:
    """Represents a connection to a VPS server"""
    server_id: int
    connection_id: str
    
    def execute_sql(self, query: str, params: tuple) -> List[tuple]:
        """Execute SQL query on the server"""
        # Implementation will be in the module
        raise NotImplementedError
    
    def close(self) -> None:
        """Close the connection"""
        raise NotImplementedError
    
    def is_alive(self) -> bool:
        """Check if connection is still active"""
        raise NotImplementedError


class VPSManagementInterface:
    """
    Public interface for VPS Management Module.
    
    This interface provides controlled access to server and domain functionality
    for other modules. All methods include validation, error handling, and audit logging.
    """
    
    def __init__(self, module: 'VPSModule'):
        self._module = module
    
    # Server Methods
    
    def get_server_info(self, server_id: int) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific server.
        
        Args:
            server_id: Unique identifier of the server
            
        Returns:
            Dict containing server information:
            - id: Server ID
            - hostname: Server hostname
            - ip_address: Server IP
            - status: active/inactive/maintenance
            - type: Server type (postfix-dovecot, etc)
            - domain_count: Number of domains
            - created_at: Creation timestamp
            - last_check: Last connectivity check
            - is_available: Availability status
            
        Raises:
            ServerNotFoundError: If server_id doesn't exist
            PermissionError: If caller lacks read permission
        """
        return self._module._get_server_info_impl(server_id)
    
    def get_server_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Find which server hosts a specific domain.
        
        Args:
            domain: Fully qualified domain name
            
        Returns:
            Server info dict (same as get_server_info) or None if not found
        """
        return self._module._get_server_by_domain_impl(domain)
    
    def list_active_servers(self) -> List[Dict[str, Any]]:
        """
        Get all servers with 'active' status.
        
        Returns:
            List of server info dicts with summary data:
            - id: Server ID
            - hostname: Server hostname
            - ip_address: Server IP
            - domain_count: Number of domains
            - mailbox_capacity: Max mailboxes
            - current_load: Load percentage (0.0-1.0)
        """
        return self._module._list_active_servers_impl()
    
    def get_server_connection(self, server_id: int) -> ServerConnection:
        """
        Get a secure connection object for server operations.
        
        Args:
            server_id: Server to connect to
            
        Returns:
            ServerConnection object (pre-authenticated)
            
        Important:
            - Caller MUST close connection after use
            - Connection times out after 5 minutes
            - Max 10 concurrent connections per module
            
        Raises:
            ServerNotFoundError: If server doesn't exist
            ConnectionFailureError: If connection fails
        """
        return self._module._get_server_connection_impl(server_id)
    
    def verify_server_connectivity(self, server_id: int) -> bool:
        """
        Test if server is reachable and responsive.
        
        Args:
            server_id: Server to test
            
        Returns:
            True if all connectivity tests pass, False otherwise
            
        Tests performed:
            1. SSH connectivity
            2. Database connection
            3. Mail service response
            
        Rate limit: Max 1 per server per minute
        """
        return self._module._verify_server_connectivity_impl(server_id)
    
    # Domain Methods
    
    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """
        Retrieve domain configuration and DNS records.
        
        Args:
            domain: Domain name to query
            
        Returns:
            Dict containing:
            - domain: Domain name
            - server_id: Hosting server ID
            - server_hostname: Server hostname
            - mx_records: List of MX records
            - spf_record: SPF record string
            - dkim_selector: DKIM selector
            - dkim_public_key: DKIM public key
            - verification_status: verified/pending/failed
            - verified_at: Verification timestamp
            
        Raises:
            DomainNotFoundError: If domain doesn't exist
        """
        return self._module._get_domain_info_impl(domain)
    
    def list_domains_for_server(self, server_id: int) -> List[str]:
        """
        Get all domains associated with a server.
        
        Args:
            server_id: Server identifier
            
        Returns:
            List of domain names
            
        Raises:
            ServerNotFoundError: If server doesn't exist
        """
        return self._module._list_domains_for_server_impl(server_id)