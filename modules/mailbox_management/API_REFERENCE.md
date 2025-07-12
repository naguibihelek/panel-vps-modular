# Mailbox Management Module - API Reference

## Interface Class: MailboxManagementInterface

### Overview
The Mailbox Management Interface provides controlled access to mailbox functionality for other modules. All methods include validation, error handling, and proper event emission.

### Import
```python
from modules.mailbox_management.interface import MailboxManagementInterface

# Initialize
mailbox_interface = MailboxManagementInterface()
```

## Mailbox Methods

### get_mailbox_info(mailbox_id: int) -> Dict[str, Any]
Retrieve detailed information about a specific mailbox.

**Parameters:**
- `mailbox_id` (int): Unique identifier of the mailbox

**Returns:**
```python
{
    'id': 1,
    'email': 'john@example.com',
    'server_id': 1,
    'server_hostname': 'mail1.example.com',
    'auth_type': 'oauth',  # or 'password'
    'oauth_provider': 'google',  # if oauth
    'first_name': 'John',
    'last_name': 'Doe',
    'company_name': 'Acme Inc',
    'warmup_enabled': True,
    'warmup_day': 15,
    'daily_quota': 300,
    'quota_used_today': 150,
    'status': 'active',
    'created_at': '2024-01-15T10:30:00Z',
    'last_activity': '2024-07-11T09:15:00Z'
}
```

**Exceptions:**
- `MailboxNotFoundError`: If mailbox_id doesn't exist
- `PermissionError`: If caller lacks read permission

---

### get_mailbox_by_email(email: str) -> Dict[str, Any]
Find mailbox information by email address.

**Parameters:**
- `email` (str): Email address to search for

**Returns:**
- Mailbox info dict (same as get_mailbox_info)
- `None` if email not found

**Example:**
```python
mailbox = mailbox_interface.get_mailbox_by_email('john@example.com')
if mailbox:
    print(f"Mailbox on server: {mailbox['server_hostname']}")
```

---

### list_active_mailboxes() -> List[Dict[str, Any]]
Get all mailboxes with 'active' status.

**Parameters:** None

**Returns:**
```python
[
    {
        'id': 1,
        'email': 'john@example.com',
        'server_id': 1,
        'warmup_enabled': True,
        'daily_quota': 300,
        'quota_used_today': 150,
        'auth_type': 'oauth',
        'last_activity': '2024-07-11T09:15:00Z'
    },
    # ... more mailboxes
]
```

**Use Case:** Campaign targeting, warmup pairing

---

### list_mailboxes_for_server(server_id: int) -> List[Dict[str, Any]]
Get all mailboxes on a specific server.

**Parameters:**
- `server_id` (int): Server identifier

**Returns:**
```python
[
    {
        'id': 1,
        'email': 'john@example.com',
        'warmup_enabled': True,
        'daily_quota': 300,
        'status': 'active'
    },
    # ... more mailboxes
]
```

**Use Case:** Server capacity planning, migration

---

### get_mailbox_credentials(mailbox_id: int) -> Dict[str, Any]
Retrieve decrypted credentials for mailbox access.

**Parameters:**
- `mailbox_id` (int): Mailbox identifier

**Returns:**
```python
# For password authentication:
{
    'auth_type': 'password',
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_encryption': 'STARTTLS',
    'smtp_username': 'john@example.com',
    'smtp_password': 'decrypted_password',
    'imap_host': 'imap.gmail.com',
    'imap_port': 993,
    'imap_encryption': 'SSL',
    'imap_username': 'john@example.com',
    'imap_password': 'decrypted_password'
}

# For OAuth authentication:
{
    'auth_type': 'oauth',
    'provider': 'google',
    'email': 'john@example.com',
    'access_token': 'decrypted_access_token',
    'refresh_token': 'decrypted_refresh_token',
    'token_expiry': '2024-07-11T15:30:00Z',
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'imap_host': 'imap.gmail.com',
    'imap_port': 993
}
```

**Security:**
- Credentials are decrypted only for the requesting module
- Access is logged for audit
- Rate limited to prevent abuse

**Exceptions:**
- `MailboxNotFoundError`: Invalid mailbox_id
- `CredentialError`: Decryption failure
- `PermissionError`: Unauthorized access

---

### check_mailbox_quota(mailbox_id: int) -> Dict[str, Any]
Check current quota usage for a mailbox.

**Parameters:**
- `mailbox_id` (int): Mailbox identifier

**Returns:**
```python
{
    'daily_quota': 300,
    'used_today': 150,
    'remaining_today': 150,
    'percentage_used': 50.0,
    'reset_time': '2024-07-12T00:00:00Z',
    'is_exceeded': False,
    'can_send': True
}
```

**Use Case:** Pre-send validation, quota enforcement

---

### is_warmup_enabled(mailbox_id: int) -> bool
Quick check if warmup is active for a mailbox.

**Parameters:**
- `mailbox_id` (int): Mailbox identifier

**Returns:**
- `True` if warmup is enabled
- `False` if disabled or mailbox not found

**Example:**
```python
if mailbox_interface.is_warmup_enabled(1):
    # Include in warmup rotation
    pass
```

---

### get_oauth_config(domain: str) -> Dict[str, Any]
Get OAuth configuration for a domain.

**Parameters:**
- `domain` (str): Domain name

**Returns:**
```python
{
    'id': 1,
    'provider': 'google',
    'domain': 'example.com',
    'client_id': 'client_id_value',
    'redirect_uri': 'https://panel.example.com/oauth/callback',
    'scopes': ['https://www.googleapis.com/auth/gmail.send'],
    'configured_at': '2024-07-01T10:00:00Z',
    'mailbox_count': 25
}
```

**Note:** Client secret is never exposed through interface

## Bulk Operations

### create_mailboxes_bulk(mailboxes: List[Dict]) -> Dict[str, Any]
Create multiple mailboxes in one operation.

**Parameters:**
- `mailboxes` (List[Dict]): List of mailbox configurations

**Input Format:**
```python
[
    {
        'email': 'john@example.com',
        'password': 'secure_password',  # if not OAuth
        'server_id': 1,
        'oauth_config_id': 1,  # if OAuth
        'first_name': 'John',
        'last_name': 'Doe',
        'company_name': 'Acme Inc',
        'warmup_enabled': True,
        'daily_quota': 300
    },
    # ... more mailboxes
]
```

**Returns:**
```python
{
    'total': 10,
    'successful': 8,
    'failed': 2,
    'created_ids': [1, 2, 3, 4, 5, 6, 7, 8],
    'errors': [
        {'email': 'duplicate@example.com', 'error': 'Email already exists'},
        {'email': 'invalid@', 'error': 'Invalid email format'}
    ]
}
```

**Limits:** Maximum 1000 mailboxes per call

## Event Subscriptions

### Available Events

Other modules can subscribe to these events:

```python
from shared.events import subscribe

# Subscribe to mailbox creation
@subscribe('mailbox.created')
def handle_new_mailbox(event_data):
    mailbox_id = event_data['mailbox_id']
    email = event_data['email']
    warmup_enabled = event_data['warmup_enabled']
    # React to new mailbox
```

**Events:**
- `mailbox.created` - New mailbox added
- `mailbox.updated` - Settings changed
- `mailbox.deleted` - Mailbox removed
- `mailbox.warmup_enabled` - Warmup activated
- `mailbox.warmup_disabled` - Warmup deactivated
- `mailbox.quota_changed` - Daily limit updated
- `mailbox.quota_exceeded` - Over daily limit
- `oauth.configured` - OAuth setup complete
- `oauth.token_refreshed` - Token updated

**Event Data Format:**
```python
{
    'mailbox_id': 1,
    'email': 'john@example.com',
    'timestamp': '2024-07-11T10:30:00Z',
    'changes': {  # for update events
        'warmup_enabled': {'old': False, 'new': True}
    }
}
```

## Error Handling

### Exception Hierarchy
```
MailboxManagementError (base)
├── MailboxNotFoundError
├── DuplicateEmailError
├── CredentialError
├── OAuthError
│   ├── OAuthConfigError
│   ├── TokenRefreshError
│   └── AuthorizationError
├── QuotaExceededError
├── ServerCapacityError
└── ValidationError
```

### Example Error Handling
```python
from modules.mailbox_management.exceptions import (
    MailboxNotFoundError,
    QuotaExceededError,
    OAuthError
)

try:
    credentials = mailbox_interface.get_mailbox_credentials(999)
except MailboxNotFoundError:
    # Handle missing mailbox
    pass
except OAuthError as e:
    # Handle OAuth-specific issues
    if isinstance(e, TokenRefreshError):
        # Attempt manual refresh
        pass
```

## Rate Limits

To ensure system stability:

- `get_mailbox_credentials`: Max 100 calls/minute per module
- `create_mailboxes_bulk`: Max 10 calls/minute
- `check_mailbox_quota`: Max 1000 calls/minute
- OAuth operations: Max 20 calls/minute per domain

## Best Practices

1. **Cache mailbox info when possible**
   ```python
   # Good: Cache for repeated use
   mailbox_info = mailbox_interface.get_mailbox_info(1)
   # Use cached info multiple times
   
   # Bad: Repeated calls
   for i in range(10):
       info = mailbox_interface.get_mailbox_info(1)
   ```

2. **Handle OAuth token refresh**
   ```python
   credentials = mailbox_interface.get_mailbox_credentials(1)
   if credentials['auth_type'] == 'oauth':
       expiry = datetime.fromisoformat(credentials['token_expiry'])
       if expiry - datetime.now() < timedelta(minutes=5):
           # Token expiring soon, prepare for refresh
           pass
   ```

3. **Check quotas before sending**
   ```python
   quota = mailbox_interface.check_mailbox_quota(1)
   if quota['can_send'] and quota['remaining_today'] >= emails_to_send:
       # Safe to proceed
       pass
   ```

4. **Use bulk operations for efficiency**
   ```python
   # Good: Single bulk call
   result = mailbox_interface.create_mailboxes_bulk(mailbox_list)
   
   # Bad: Individual calls in loop
   for mailbox in mailbox_list:
       create_single_mailbox(mailbox)
   ```

5. **Subscribe to events instead of polling**
   ```python
   # Good: React to quota changes
   @subscribe('mailbox.quota_exceeded')
   def pause_campaigns(data):
       # Stop sending for this mailbox
       pass
   ```

---

**Version**: 1.0.0  
**Interface Stability**: Stable  
**Last Updated**: July 2024