# Mailbox Management Module

## Quick Overview

The Mailbox Management module handles all email account operations including creation, credential management, OAuth integration, and warmup coordination. This module is essential for managing the email infrastructure that powers campaigns and warmup operations.

## Key Responsibilities
- 📧 Create and manage email mailboxes
- 🔐 Handle OAuth and password authentication
- 🔑 Secure credential storage and retrieval
- 📊 Track mailbox quotas and usage
- 🔥 Initialize warmup for new mailboxes
- 📤 Bulk import/export operations

## Module Status
- **Version**: 1.0.0
- **Stability**: Stable
- **Dependencies**: Core Foundation, VPS Management
- **Required By**: Warmup Engine, Campaign System

## Quick Start

### For Module Users (Other Modules)
```python
from modules.mailbox_management.interface import MailboxManagementInterface

mailbox = MailboxManagementInterface()

# Get mailbox details
info = mailbox.get_mailbox_info(1)

# Check if warmup is enabled
if mailbox.is_warmup_enabled(1):
    # Include in warmup rotation
    pass

# Get credentials for sending
creds = mailbox.get_mailbox_credentials(1)
```

### For Administrators

1. **Add Single Mailbox**: `/mailbox/add`
2. **Bulk Import**: `/mailbox/bulk`
3. **OAuth Setup**: `/mailbox/oauth/configure`
4. **View All**: `/mailbox/list`

## Documentation

- 📋 [Module Scope](MODULE_SCOPE.md) - Detailed boundaries and responsibilities
- 🔧 [Features](FEATURES.md) - Complete feature list
- 📚 [API Reference](API_REFERENCE.md) - Interface documentation

## Database Tables

This module owns:
- `mailboxes` - Email account configurations
- `oauth_configs` - OAuth provider settings
- `mailbox_credentials` - Encrypted tokens/passwords
- `mailbox_warmup_settings` - Warmup configurations

## Security Notes

- All passwords and tokens are encrypted using Core encryption
- OAuth tokens are automatically refreshed before expiry
- Credential access is logged and rate-limited
- Support for both password and OAuth authentication

## Common Operations

### Check Mailbox Quota
```python
quota = mailbox.check_mailbox_quota(mailbox_id)
if quota['remaining_today'] > 0:
    print(f"Can send {quota['remaining_today']} more emails today")
```

### Bulk Create Mailboxes
```python
mailboxes = [
    {
        'email': 'user1@example.com',
        'server_id': 1,
        'warmup_enabled': True,
        'daily_quota': 300
    },
    # ... more mailboxes
]

result = mailbox.create_mailboxes_bulk(mailboxes)
print(f"Created {result['successful']} of {result['total']} mailboxes")
```

### Get OAuth Config
```python
oauth = mailbox.get_oauth_config('example.com')
if oauth:
    print(f"OAuth configured with {oauth['provider']}")
```

## Events

### Emitted Events
- `mailbox.created`
- `mailbox.updated`
- `mailbox.deleted`
- `mailbox.warmup_enabled`
- `mailbox.warmup_disabled`
- `mailbox.quota_exceeded`
- `oauth.token_refreshed`

### Subscribe to Events
```python
from shared.events import subscribe

@subscribe('mailbox.quota_exceeded')
def handle_quota_exceeded(event_data):
    # Pause campaigns for this mailbox
    mailbox_id = event_data['mailbox_id']
    pause_campaigns(mailbox_id)
```

## Troubleshooting

### Authentication Failed
1. Check mailbox credentials are current
2. For OAuth, verify token hasn't expired
3. Test connection manually
4. Review `/var/log/mailbox_management.log`

### Bulk Import Issues
1. Verify CSV format matches template
2. Check for duplicate emails
3. Ensure servers have capacity
4. Review error report for specifics

### OAuth Token Errors
1. Check OAuth config is valid
2. Verify scopes are sufficient
3. Try manual re-authorization
4. Check provider-specific requirements

## Warmup Integration

When creating mailboxes with warmup enabled:
1. Mailbox is automatically initialized with warmup stats
2. Daily quota is set (default 300)
3. Warmup day starts at 1
4. Included in warmup rotation immediately

## Support

- 📝 Log Location: `/var/log/mailbox_management/`
- 🐛 Report Issues: Create ticket with module tag
- 📧 Module Owner: Email Infrastructure Team

---

For development and contribution guidelines, see the main [ARCHITECTURE.md](/root/ARCHITECTURE.md) document.