# VPS Management Module - Scope Definition

## Module Purpose
The VPS Management module is responsible for managing mail server infrastructure, including server configurations, domain management, and DNS settings. This module provides the foundation for all email operations by managing the physical servers where mailboxes reside.

## Core Responsibilities

### 1. Server Management
- Register and track mail VPS servers
- Store server connection credentials (encrypted)
- Monitor server status and availability
- Manage server metadata (IP, hostname, capabilities)
- Handle server decommissioning

### 2. Domain Management
- Associate domains with servers
- Track MX record configurations
- Manage domain ownership and verification
- Handle multi-domain per server scenarios
- Domain status monitoring

### 3. DNS Configuration
- MX record management
- SPF record configuration
- DKIM settings storage
- DMARC policy management
- DNS propagation tracking

### 4. Security & Access
- Encrypted credential storage for server access
- SSH key management
- Database connection security
- API access control
- Audit trail for server changes

## Module Boundaries

### What This Module OWNS:
- `servers` database table
- `domains` database table  
- `dns_records` database table
- `server_credentials` database table
- Server connection logic
- Domain verification logic

### What This Module DOES NOT Handle:
- Creating mailboxes (Mailbox Management module)
- Sending emails (Warmup/Campaign modules)
- User authentication (Core Foundation)
- Email content (Campaign module)
- Response processing (Integrations module)

## Data Models

### Server Model
```
- id: Primary key
- hostname: Server FQDN
- ip_address: IPv4/IPv6 address
- ssh_port: SSH connection port
- db_host: Database hostname
- db_port: Database port
- db_name: Mail database name
- db_username: Database username (encrypted)
- db_password: Database password (encrypted)
- server_type: Type of mail server software
- status: active/inactive/maintenance
- created_at: Timestamp
- updated_at: Timestamp
```

### Domain Model
```
- id: Primary key
- server_id: Foreign key to servers
- domain_name: FQDN
- mx_records: JSON array of MX records
- spf_record: SPF TXT record
- dkim_selector: DKIM selector
- dkim_public_key: DKIM public key
- dmarc_policy: DMARC policy string
- verification_status: verified/pending/failed
- created_at: Timestamp
- updated_at: Timestamp
```

## Interface Methods

### Public API (for other modules)
```python
class VPSManagementInterface:
    def get_server_info(server_id: int) -> Dict
    def get_server_by_domain(domain: str) -> Dict
    def list_active_servers() -> List[Dict]
    def get_server_connection(server_id: int) -> Connection
    def verify_server_connectivity(server_id: int) -> bool
    def get_domain_info(domain: str) -> Dict
    def list_domains_for_server(server_id: int) -> List[str]
```

### Events Emitted
- `server.created` - New server added
- `server.updated` - Server configuration changed
- `server.deleted` - Server removed
- `server.status_changed` - Server status update
- `domain.added` - New domain configured
- `domain.verified` - Domain verification complete
- `domain.removed` - Domain deleted

### Events Subscribed To
- None (this is a foundational module)

## Security Requirements

1. **Credential Encryption**
   - All passwords encrypted using Core encryption service
   - No plaintext passwords in database or logs
   - Encryption keys never exposed to this module

2. **Access Control**
   - Only admin users can add/modify servers
   - Read access for server info to other modules
   - Connection credentials only via secure interface

3. **Audit Trail**
   - Log all server modifications
   - Track who accessed server credentials
   - Monitor failed connection attempts

## Performance Requirements

- Server list retrieval: < 100ms
- Connection establishment: < 5s
- Domain verification: < 30s
- Bulk operations support for domains

## Dependencies

### On Core Foundation:
- Database service for data persistence
- Encryption service for credential security
- Authentication service for access control
- Logging service for audit trail

### External Dependencies:
- MySQL connector for mail server databases
- SSH library for server connections
- DNS resolver for domain verification

## Error Handling

1. **Connection Failures**
   - Retry logic with exponential backoff
   - Alert on repeated failures
   - Graceful degradation

2. **Invalid Credentials**
   - Log attempts
   - Lock after repeated failures
   - Admin notification

3. **Domain Verification Failures**
   - Detailed error messages
   - Suggested corrections
   - Manual override option

## Future Enhancements (Out of Current Scope)

- Automated server provisioning
- Load balancing across servers
- Geo-distributed server management
- Automated SSL certificate management
- Server performance monitoring
- Capacity planning tools

---

**Version**: 1.0.0  
**Status**: Final  
**Last Updated**: July 2024