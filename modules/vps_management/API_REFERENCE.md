# VPS Management Module - API Reference

## Interface Class: VPSManagementInterface

### Overview
The VPS Management Interface provides controlled access to server and domain functionality for other modules. All methods include validation, error handling, and audit logging.

### Import
```python
from modules.vps_management.interface import VPSManagementInterface

# Initialize
vps_interface = VPSManagementInterface()
```

## Server Methods

### get_server_info(server_id: int) -> Dict[str, Any]
Retrieve detailed information about a specific server.

**Parameters:**
- `server_id` (int): Unique identifier of the server

**Returns:**
```python
{
    'id': 1,
    'hostname': 'mail1.example.com',
    'ip_address': '192.168.1.100',
    'status': 'active',
    'type': 'postfix-dovecot',
    'domain_count': 5,
    'created_at': '2024-01-15T10:30:00Z',
    'last_check': '2024-07-10T15:45:00Z',
    'is_available': True
}
```

**Exceptions:**
- `ServerNotFoundError`: If server_id doesn't exist
- `PermissionError`: If caller lacks read permission

---

### get_server_by_domain(domain: str) -> Dict[str, Any]
Find which server hosts a specific domain.

**Parameters:**
- `domain` (str): Fully qualified domain name

**Returns:**
- Server info dict (same as get_server_info)
- `None` if domain not found

**Example:**
```python
server = vps_interface.get_server_by_domain('example.com')
if server:
    print(f"Domain hosted on: {server['hostname']}")
```

---

### list_active_servers() -> List[Dict[str, Any]]
Get all servers with 'active' status.

**Parameters:** None

**Returns:**
```python
[
    {
        'id': 1,
        'hostname': 'mail1.example.com',
        'ip_address': '192.168.1.100',
        'domain_count': 5,
        'mailbox_capacity': 1000,
        'current_load': 0.45
    },
    # ... more servers
]
```

**Use Case:** Load balancing, server selection

---

### get_server_connection(server_id: int) -> ServerConnection
Get a secure connection object for server operations.

**Parameters:**
- `server_id` (int): Server to connect to

**Returns:**
```python
class ServerConnection:
    def execute_sql(query: str, params: tuple) -> ResultSet
    def close() -> None
    def is_alive() -> bool
```

**Important:** 
- Connection is pre-authenticated
- Caller MUST close connection after use
- Connection times out after 5 minutes

**Example:**
```python
conn = vps_interface.get_server_connection(1)
try:
    result = conn.execute_sql("SELECT COUNT(*) FROM users", ())
    print(f"Mailbox count: {result[0][0]}")
finally:
    conn.close()
```

---

### verify_server_connectivity(server_id: int) -> bool
Test if server is reachable and responsive.

**Parameters:**
- `server_id` (int): Server to test

**Returns:**
- `True` if all connectivity tests pass
- `False` if any test fails

**Tests Performed:**
1. SSH connectivity
2. Database connection
3. Mail service response

**Example:**
```python
if not vps_interface.verify_server_connectivity(1):
    # Handle server downtime
    pass
```

## Domain Methods

### get_domain_info(domain: str) -> Dict[str, Any]
Retrieve domain configuration and DNS records.

**Parameters:**
- `domain` (str): Domain name to query

**Returns:**
```python
{
    'domain': 'example.com',
    'server_id': 1,
    'server_hostname': 'mail1.example.com',
    'mx_records': [
        {'priority': 10, 'host': 'mail1.example.com'},
        {'priority': 20, 'host': 'mail2.example.com'}
    ],
    'spf_record': 'v=spf1 mx ~all',
    'dkim_selector': 'default',
    'dkim_public_key': 'k=rsa; p=MIGfMA0...',
    'verification_status': 'verified',
    'verified_at': '2024-07-01T12:00:00Z'
}
```

**Exceptions:**
- `DomainNotFoundError`: If domain doesn't exist

---

### list_domains_for_server(server_id: int) -> List[str]
Get all domains associated with a server.

**Parameters:**
- `server_id` (int): Server identifier

**Returns:**
```python
['example.com', 'example.org', 'example.net']
```

**Use Case:** Server decommissioning checks

## Event Subscriptions

### Available Events

Other modules can subscribe to these events:

```python
from shared.events import subscribe

# Subscribe to server status changes
@subscribe('server.status_changed')
def handle_server_status(event_data):
    server_id = event_data['server_id']
    old_status = event_data['old_status']
    new_status = event_data['new_status']
    # React to status change
```

**Events:**
- `server.created` - New server added
- `server.updated` - Server config changed
- `server.deleted` - Server removed
- `server.status_changed` - Status update
- `domain.added` - New domain
- `domain.verified` - Domain verified
- `domain.removed` - Domain deleted

## Error Handling

### Exception Hierarchy
```
VPSManagementError (base)
├── ServerNotFoundError
├── DomainNotFoundError
├── ConnectionFailureError
├── CredentialError
├── ValidationError
└── PermissionError
```

### Example Error Handling
```python
from modules.vps_management.exceptions import (
    ServerNotFoundError,
    ConnectionFailureError
)

try:
    info = vps_interface.get_server_info(999)
except ServerNotFoundError:
    # Handle missing server
    pass
except ConnectionFailureError as e:
    # Handle connection issues
    logger.error(f"Connection failed: {e}")
```

## Rate Limits

To prevent abuse and ensure stability:

- `get_server_connection`: Max 10 concurrent per module
- `verify_server_connectivity`: Max 1 per server per minute
- Bulk operations: Max 100 items per request

## Best Practices

1. **Always close connections**
   ```python
   conn = vps_interface.get_server_connection(1)
   try:
       # Do work
   finally:
       conn.close()
   ```

2. **Cache server info when possible**
   ```python
   # Don't call in tight loops
   server_info = vps_interface.get_server_info(1)
   # Reuse server_info
   ```

3. **Handle all exceptions**
   ```python
   try:
       servers = vps_interface.list_active_servers()
   except VPSManagementError as e:
       # Graceful degradation
       servers = []
   ```

4. **Subscribe to events instead of polling**
   ```python
   # Good: React to events
   @subscribe('server.status_changed')
   def on_status_change(data):
       # Handle change
   
   # Bad: Polling
   while True:
       status = vps_interface.get_server_info(1)['status']
       time.sleep(60)
   ```

---

**Version**: 1.0.0  
**Interface Stability**: Stable  
**Last Updated**: July 2024