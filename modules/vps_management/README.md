# VPS Management Module

## Quick Overview

The VPS Management module handles all mail server infrastructure, including server registration, domain management, and DNS configuration. This is a foundational module that other modules depend on for server access.

## Key Responsibilities
- 🖥️ Register and manage mail VPS servers
- 🌐 Configure domains and DNS records  
- 🔐 Secure credential storage
- 🔍 Monitor server connectivity
- 📊 Provide server information to other modules

## Module Status
- **Version**: 1.0.0
- **Stability**: Stable
- **Dependencies**: Core Foundation only
- **Required By**: Mailbox Management, Warmup Engine, Campaign System

## Quick Start

### For Module Users (Other Modules)
```python
from modules.vps_management.interface import VPSManagementInterface

vps = VPSManagementInterface()

# Get server info
server = vps.get_server_info(1)

# Find server for domain
server = vps.get_server_by_domain('example.com')

# List active servers
servers = vps.list_active_servers()
```

### For Administrators

1. **Add a Server**: `/vps/servers/add`
2. **Configure Domain**: `/vps/domains/add`
3. **Check Status**: `/vps/status`

## Documentation

- 📋 [Module Scope](MODULE_SCOPE.md) - Detailed boundaries and responsibilities
- 🔧 [Features](FEATURES.md) - Complete feature list
- 📚 [API Reference](API_REFERENCE.md) - Interface documentation

## Database Tables

This module owns:
- `servers` - Server configurations
- `domains` - Domain associations
- `dns_records` - DNS configurations
- `server_credentials` - Encrypted credentials

## Security Notes

- All credentials are encrypted using Core encryption service
- No plaintext passwords are ever stored or logged
- Access is audited and logged
- SSH keys preferred over passwords

## Common Operations

### Test Server Connection
```python
if vps.verify_server_connectivity(server_id):
    print("Server is online")
else:
    print("Server is unreachable")
```

### Get Connection for Direct Access
```python
conn = vps.get_server_connection(server_id)
try:
    # Perform database operations
    result = conn.execute_sql("SELECT ...", params)
finally:
    conn.close()  # Always close!
```

## Events

### Emitted Events
- `server.created`
- `server.updated`
- `server.deleted`
- `server.status_changed`
- `domain.added`
- `domain.verified`
- `domain.removed`

### Subscribe to Events
```python
from shared.events import subscribe

@subscribe('server.status_changed')
def handle_status_change(event_data):
    # React to server status changes
    pass
```

## Troubleshooting

### Server Connection Failed
1. Check server status in UI
2. Verify credentials are correct
3. Check network connectivity
4. Review `/var/log/vps_management.log`

### Domain Verification Failed
1. Ensure DNS propagation complete (24-48h)
2. Verify MX records point to correct server
3. Check SPF/DKIM configuration
4. Use manual verification override if needed

## Support

- 📝 Log Location: `/var/log/vps_management/`
- 🐛 Report Issues: Create ticket with module tag
- 📧 Module Owner: Infrastructure Team

---

For development and contribution guidelines, see the main [ARCHITECTURE.md](/root/ARCHITECTURE.md) document.