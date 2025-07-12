"""
VPS Management Module

Handles all mail server infrastructure including servers, domains, and DNS settings.
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from shared.interfaces import BaseModule
from .interface import VPSManagementInterface, ServerConnection
from .exceptions import (
    ServerNotFoundError,
    DomainNotFoundError,
    ConnectionFailureError,
    CredentialError,
    ValidationError,
    PermissionError
)


class VPSModule(BaseModule):
    """
    Implementation of VPS Management Module.
    
    This module manages mail server infrastructure, domains, and DNS configurations.
    It provides the foundation for all email operations.
    """
    
    MODULE_NAME = "vps_management"
    MODULE_VERSION = "1.0.0"
    MODULE_DESCRIPTION = "Manages mail server infrastructure, domains, and DNS settings"
    
    def __init__(self):
        """Initialize the module"""
        super().__init__(
            self.MODULE_NAME,
            self.MODULE_VERSION,
            self.MODULE_DESCRIPTION
        )
        
        # Module-specific initialization
        self._interface = None
        self._event_handlers = []
        self._connection_pool = {}
        self._connection_count = {}
        self._max_connections_per_module = 10
        
        # Cache for performance
        self._server_cache = {}
        self._domain_cache = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Stats tracking
        self._stats = {
            "server_queries": 0,
            "domain_queries": 0,
            "connection_created": 0,
            "connection_failures": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    # Required abstract method implementations
    
    def _get_dependencies(self) -> List[str]:
        """List modules this module depends on"""
        return []  # VPS Management is a foundational module
    
    def _get_provides(self) -> List[str]:
        """List services this module provides"""
        return ["server_info", "domain_management", "server_connections"]
    
    def _get_consumes(self) -> List[str]:
        """List services this module consumes"""
        return ["database", "encryption", "authentication"]
    
    def _initialize(self) -> bool:
        """Module-specific initialization"""
        try:
            self.logger.info("Initializing VPS Management module")
            
            # Create interface
            self._interface = VPSManagementInterface(self)
            
            # Initialize database tables if needed
            self._init_database()
            
            # Load configuration
            self._load_config()
            
            # Clear caches
            self._server_cache.clear()
            self._domain_cache.clear()
            
            return True
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    def _start(self) -> bool:
        """Module-specific start logic"""
        try:
            self.logger.info("Starting VPS Management services")
            
            # Register event handlers
            self._register_event_handlers()
            
            # Emit module started event
            self.event_bus.emit(
                "module.started",
                {"module": self.MODULE_NAME},
                source=self.MODULE_NAME
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Start failed: {e}")
            return False
    
    def _stop(self) -> bool:
        """Module-specific stop logic"""
        try:
            self.logger.info("Stopping VPS Management services")
            
            # Close all connections
            self._close_all_connections()
            
            # Unregister event handlers
            self._unregister_event_handlers()
            
            # Clear caches
            self._server_cache.clear()
            self._domain_cache.clear()
            
            return True
        except Exception as e:
            self.logger.error(f"Stop failed: {e}")
            return False
    
    def _health_check(self) -> Dict[str, Any]:
        """Module-specific health check"""
        health_details = {
            "server_cache_size": len(self._server_cache),
            "domain_cache_size": len(self._domain_cache),
            "active_connections": sum(self._connection_count.values()),
            "total_servers": self._count_total_servers(),
            "active_servers": self._count_active_servers(),
            "cache_hit_rate": self._calculate_cache_hit_rate()
        }
        
        # Check database connectivity
        try:
            with self.db.get_session() as session:
                session.execute("SELECT 1")
            health_details["database"] = "healthy"
        except Exception:
            health_details["database"] = "unhealthy"
        
        return health_details
    
    def _get_stats(self) -> Dict[str, Any]:
        """Module-specific statistics"""
        return {
            **self._stats,
            "cache_size": len(self._server_cache) + len(self._domain_cache),
            "active_connections": sum(self._connection_count.values()),
            "connection_pool_size": len(self._connection_pool)
        }
    
    def _register_event_handlers(self):
        """Register module event handlers"""
        # VPS Management is foundational - doesn't subscribe to other module events
        pass
    
    def _unregister_event_handlers(self):
        """Unregister module event handlers"""
        for event_name, handler in self._event_handlers:
            self.event_bus.off(event_name, handler)
        self._event_handlers.clear()
    
    def get_interface(self) -> VPSManagementInterface:
        """Get the public interface for this module"""
        return self._interface
    
    # Internal implementation methods
    
    def _get_server_info_impl(self, server_id: int) -> Dict[str, Any]:
        """Internal implementation of get_server_info"""
        try:
            self._stats["server_queries"] += 1
            
            # Check cache first
            cache_key = f"server_{server_id}"
            if cache_key in self._server_cache:
                cache_entry = self._server_cache[cache_key]
                if (datetime.now() - cache_entry["timestamp"]).seconds < self._cache_ttl:
                    self._stats["cache_hits"] += 1
                    return cache_entry["data"]
            
            self._stats["cache_misses"] += 1
            
            # Query database
            with self.db.get_session() as session:
                result = session.execute(
                    "SELECT * FROM servers WHERE id = ?",
                    (server_id,)
                ).fetchone()
                
                if not result:
                    raise ServerNotFoundError(f"Server {server_id} not found")
                
                # Get domain count
                domain_count = session.execute(
                    "SELECT COUNT(*) FROM domains WHERE server_id = ?",
                    (server_id,)
                ).fetchone()[0]
                
                server_info = {
                    "id": result["id"],
                    "hostname": result["hostname"],
                    "ip_address": result["ip_address"],
                    "status": result["status"],
                    "type": result["server_type"],
                    "domain_count": domain_count,
                    "created_at": result["created_at"].isoformat(),
                    "last_check": result["last_check"].isoformat() if result["last_check"] else None,
                    "is_available": result["status"] == "active"
                }
                
                # Cache the result
                self._server_cache[cache_key] = {
                    "data": server_info,
                    "timestamp": datetime.now()
                }
                
                return server_info
                
        except ServerNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get server info: {e}")
            raise
    
    def _get_server_by_domain_impl(self, domain: str) -> Optional[Dict[str, Any]]:
        """Internal implementation of get_server_by_domain"""
        try:
            self._stats["domain_queries"] += 1
            
            with self.db.get_session() as session:
                result = session.execute(
                    "SELECT server_id FROM domains WHERE domain_name = ?",
                    (domain,)
                ).fetchone()
                
                if not result:
                    return None
                
                return self._get_server_info_impl(result["server_id"])
                
        except Exception as e:
            self.logger.error(f"Failed to get server by domain: {e}")
            return None
    
    def _list_active_servers_impl(self) -> List[Dict[str, Any]]:
        """Internal implementation of list_active_servers"""
        try:
            with self.db.get_session() as session:
                results = session.execute(
                    """
                    SELECT s.*, COUNT(d.id) as domain_count
                    FROM servers s
                    LEFT JOIN domains d ON s.id = d.server_id
                    WHERE s.status = 'active'
                    GROUP BY s.id
                    """
                ).fetchall()
                
                servers = []
                for row in results:
                    servers.append({
                        "id": row["id"],
                        "hostname": row["hostname"],
                        "ip_address": row["ip_address"],
                        "domain_count": row["domain_count"],
                        "mailbox_capacity": row.get("mailbox_capacity", 1000),
                        "current_load": 0.0  # TODO: Implement load calculation
                    })
                
                return servers
                
        except Exception as e:
            self.logger.error(f"Failed to list active servers: {e}")
            return []
    
    def _get_server_connection_impl(self, server_id: int) -> ServerConnection:
        """Internal implementation of get_server_connection"""
        try:
            # Check connection limit
            module_name = self._get_calling_module()
            if module_name not in self._connection_count:
                self._connection_count[module_name] = 0
            
            if self._connection_count[module_name] >= self._max_connections_per_module:
                raise ConnectionFailureError(
                    f"Connection limit exceeded for module {module_name}"
                )
            
            # Get server info
            server_info = self._get_server_info_impl(server_id)
            
            # TODO: Implement actual connection logic
            # For now, return a mock connection
            connection = ServerConnection(
                server_id=server_id,
                connection_id=f"conn_{server_id}_{datetime.now().timestamp()}"
            )
            
            # Track connection
            self._connection_count[module_name] += 1
            self._stats["connection_created"] += 1
            
            # Emit event
            self.event_bus.emit(
                "server.connection_created",
                {"server_id": server_id, "module": module_name},
                source=self.MODULE_NAME
            )
            
            return connection
            
        except Exception as e:
            self._stats["connection_failures"] += 1
            self.logger.error(f"Failed to create connection: {e}")
            raise ConnectionFailureError(str(e))
    
    def _verify_server_connectivity_impl(self, server_id: int) -> bool:
        """Internal implementation of verify_server_connectivity"""
        try:
            # Get server info
            server_info = self._get_server_info_impl(server_id)
            
            # TODO: Implement actual connectivity tests
            # For now, return based on status
            is_connected = server_info["status"] == "active"
            
            # Update last check timestamp
            with self.db.get_session() as session:
                session.execute(
                    "UPDATE servers SET last_check = ? WHERE id = ?",
                    (datetime.now(), server_id)
                )
            
            # Emit event if status changed
            if not is_connected:
                self.event_bus.emit(
                    "server.connectivity_failed",
                    {"server_id": server_id},
                    source=self.MODULE_NAME
                )
            
            return is_connected
            
        except Exception as e:
            self.logger.error(f"Failed to verify connectivity: {e}")
            return False
    
    def _get_domain_info_impl(self, domain: str) -> Dict[str, Any]:
        """Internal implementation of get_domain_info"""
        try:
            self._stats["domain_queries"] += 1
            
            # Check cache
            cache_key = f"domain_{domain}"
            if cache_key in self._domain_cache:
                cache_entry = self._domain_cache[cache_key]
                if (datetime.now() - cache_entry["timestamp"]).seconds < self._cache_ttl:
                    self._stats["cache_hits"] += 1
                    return cache_entry["data"]
            
            self._stats["cache_misses"] += 1
            
            with self.db.get_session() as session:
                result = session.execute(
                    "SELECT * FROM domains WHERE domain_name = ?",
                    (domain,)
                ).fetchone()
                
                if not result:
                    raise DomainNotFoundError(f"Domain {domain} not found")
                
                # Get server hostname
                server_info = self._get_server_info_impl(result["server_id"])
                
                domain_info = {
                    "domain": result["domain_name"],
                    "server_id": result["server_id"],
                    "server_hostname": server_info["hostname"],
                    "mx_records": json.loads(result["mx_records"]) if result["mx_records"] else [],
                    "spf_record": result["spf_record"],
                    "dkim_selector": result["dkim_selector"],
                    "dkim_public_key": result["dkim_public_key"],
                    "verification_status": result["verification_status"],
                    "verified_at": result["verified_at"].isoformat() if result["verified_at"] else None
                }
                
                # Cache the result
                self._domain_cache[cache_key] = {
                    "data": domain_info,
                    "timestamp": datetime.now()
                }
                
                return domain_info
                
        except DomainNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get domain info: {e}")
            raise
    
    def _list_domains_for_server_impl(self, server_id: int) -> List[str]:
        """Internal implementation of list_domains_for_server"""
        try:
            # Verify server exists
            self._get_server_info_impl(server_id)
            
            with self.db.get_session() as session:
                results = session.execute(
                    "SELECT domain_name FROM domains WHERE server_id = ?",
                    (server_id,)
                ).fetchall()
                
                return [row["domain_name"] for row in results]
                
        except ServerNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to list domains: {e}")
            return []
    
    # Helper methods
    
    def _init_database(self):
        """Initialize database tables for VPS module"""
        with self.db.get_session() as session:
            # Create servers table
            session.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hostname TEXT NOT NULL UNIQUE,
                    ip_address TEXT NOT NULL,
                    ssh_port INTEGER DEFAULT 22,
                    db_host TEXT NOT NULL,
                    db_port INTEGER DEFAULT 3306,
                    db_name TEXT NOT NULL,
                    db_username TEXT NOT NULL,
                    db_password TEXT NOT NULL,
                    server_type TEXT DEFAULT 'postfix-dovecot',
                    status TEXT DEFAULT 'active',
                    mailbox_capacity INTEGER DEFAULT 1000,
                    last_check TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create domains table
            session.execute("""
                CREATE TABLE IF NOT EXISTS domains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    domain_name TEXT NOT NULL UNIQUE,
                    mx_records TEXT,
                    spf_record TEXT,
                    dkim_selector TEXT DEFAULT 'default',
                    dkim_public_key TEXT,
                    dmarc_policy TEXT,
                    verification_status TEXT DEFAULT 'pending',
                    verified_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES servers(id)
                )
            """)
            
            # Create indexes
            session.execute("CREATE INDEX IF NOT EXISTS idx_servers_status ON servers(status)")
            session.execute("CREATE INDEX IF NOT EXISTS idx_domains_server ON domains(server_id)")
            session.execute("CREATE INDEX IF NOT EXISTS idx_domains_status ON domains(verification_status)")
    
    def _load_config(self):
        """Load module configuration"""
        self._cache_ttl = self.config.get("cache_ttl", 300)
        self._max_connections_per_module = self.config.get("max_connections_per_module", 10)
    
    def _get_calling_module(self) -> str:
        """Get the name of the module calling this interface"""
        # TODO: Implement proper caller identification
        return "unknown"
    
    def _count_total_servers(self) -> int:
        """Count total number of servers"""
        try:
            with self.db.get_session() as session:
                result = session.execute("SELECT COUNT(*) FROM servers").fetchone()
                return result[0]
        except:
            return 0
    
    def _count_active_servers(self) -> int:
        """Count number of active servers"""
        try:
            with self.db.get_session() as session:
                result = session.execute(
                    "SELECT COUNT(*) FROM servers WHERE status = 'active'"
                ).fetchone()
                return result[0]
        except:
            return 0
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self._stats["cache_hits"] + self._stats["cache_misses"]
        if total == 0:
            return 0.0
        return self._stats["cache_hits"] / total
    
    def _close_all_connections(self):
        """Close all active connections"""
        # TODO: Implement connection cleanup
        self._connection_pool.clear()
        self._connection_count.clear()


# Module registration
MODULE_CLASS = VPSModule


def get_module() -> VPSModule:
    """Factory function to create module instance"""
    return VPSModule()