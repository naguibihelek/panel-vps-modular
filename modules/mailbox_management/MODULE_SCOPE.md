# Mailbox Management Module - Scope Definition

## Module Purpose
The Mailbox Management module is responsible for creating and managing email mailboxes across all registered VPS servers. It handles mailbox lifecycle, credential management, OAuth configurations, and integration with the warmup system for new mailboxes.

## Core Responsibilities

### 1. Mailbox Lifecycle Management
- Create new mailboxes on VPS servers
- Update mailbox configurations
- Delete mailboxes and clean up data
- Track mailbox status and availability
- Handle mailbox quotas and limits

### 2. Credential Management
- Store SMTP/IMAP credentials (encrypted)
- Manage OAuth tokens and refresh
- Handle credential rotation
- Support multiple authentication methods
- Secure credential access APIs

### 3. OAuth Configuration
- Google Workspace OAuth setup
- Store OAuth client credentials
- Manage OAuth consent and tokens
- Handle token refresh automatically
- Support multiple OAuth providers

### 4. Bulk Operations
- CSV import for multiple mailboxes
- Bulk mailbox creation
- Mass configuration updates
- Bulk warmup enablement
- Export mailbox lists

### 5. Warmup Integration
- Auto-enable warmup for new mailboxes
- Initialize warmup statistics
- Set warmup quotas (300/day)
- Track warmup readiness
- Coordinate with Warmup Engine

## Module Boundaries

### What This Module OWNS:
- `mailboxes` database table
- `oauth_configs` database table
- `mailbox_credentials` database table
- `mailbox_warmup_settings` database table
- Mailbox creation/deletion logic
- OAuth flow implementation
- Credential encryption/decryption

### What This Module DOES NOT Handle:
- Actual email sending (Warmup/Campaign modules)
- Server management (VPS Management module)
- Warmup execution (Warmup Engine module)
- Campaign assignments (Campaign System module)
- Usage statistics (Reporting module)
- Email content (Campaign module)

## Data Models

### Mailbox Model
```
- id: Primary key
- email: Email address (unique)
- password_enc: Encrypted password (nullable for OAuth)
- oauth_config_id: Foreign key to oauth_configs (nullable)
- server_id: Foreign key to VPS servers
- smtp_host: SMTP server hostname
- smtp_port: SMTP port (587/465)
- smtp_encryption: TLS/SSL/STARTTLS
- imap_host: IMAP server hostname
- imap_port: IMAP port (993/143)
- first_name: Mailbox owner first name
- last_name: Mailbox owner last name
- company_name: Associated company
- warmup_enabled: Boolean flag
- daily_quota: Email limit per day (default 300)
- status: active/inactive/suspended
- created_at: Timestamp
- updated_at: Timestamp
```

### OAuth Config Model
```
- id: Primary key
- provider: oauth provider (google/microsoft)
- domain: Associated domain
- client_id: OAuth client ID
- client_secret_enc: Encrypted client secret
- redirect_uri: OAuth callback URL
- scopes: JSON array of requested scopes
- created_at: Timestamp
- updated_at: Timestamp
```

### Mailbox Credentials Model
```
- id: Primary key
- mailbox_id: Foreign key to mailboxes
- oauth_token_enc: Encrypted access token
- oauth_refresh_token_enc: Encrypted refresh token
- token_expiry: Token expiration timestamp
- credential_type: oauth/password
- updated_at: Timestamp
```

## Interface Methods

### Public API (for other modules)
```python
class MailboxManagementInterface:
    def get_mailbox_info(mailbox_id: int) -> Dict
    def get_mailbox_by_email(email: str) -> Dict
    def list_active_mailboxes() -> List[Dict]
    def list_mailboxes_for_server(server_id: int) -> List[Dict]
    def get_mailbox_credentials(mailbox_id: int) -> Dict
    def check_mailbox_quota(mailbox_id: int) -> Dict
    def is_warmup_enabled(mailbox_id: int) -> bool
    def get_oauth_config(domain: str) -> Dict
```

### Events Emitted
- `mailbox.created` - New mailbox added
- `mailbox.updated` - Mailbox settings changed
- `mailbox.deleted` - Mailbox removed
- `mailbox.warmup_enabled` - Warmup activated
- `mailbox.warmup_disabled` - Warmup deactivated
- `mailbox.quota_changed` - Daily limit updated
- `oauth.configured` - OAuth setup complete
- `oauth.token_refreshed` - OAuth token updated

### Events Subscribed To
- `server.deleted` - Remove associated mailboxes
- `server.status_changed` - Update mailbox availability

## Security Requirements

1. **Credential Encryption**
   - All passwords and tokens encrypted via Core
   - OAuth secrets never exposed in logs
   - Tokens refreshed before expiry

2. **Access Control**
   - Admin only for mailbox creation/deletion
   - Module access for credential retrieval
   - Rate limiting on credential access

3. **OAuth Security**
   - Secure token storage
   - Automatic token refresh
   - Revocation handling
   - Scope minimization

## Performance Requirements

- Mailbox creation: < 5s
- Credential retrieval: < 100ms
- Bulk import: 100 mailboxes/minute
- OAuth token refresh: < 2s
- List operations: < 200ms

## Dependencies

### On Core Foundation:
- Database service for persistence
- Encryption service for credentials
- Authentication for access control
- Event bus for notifications

### On VPS Management:
- Server information retrieval
- Server availability checks
- Connection management

### External Dependencies:
- Google OAuth libraries
- SMTP/IMAP validation libraries
- CSV parsing libraries

## Error Handling

1. **Creation Failures**
   - Duplicate email detection
   - Server capacity checks
   - Rollback on failure
   - Detailed error messages

2. **OAuth Failures**
   - Invalid credentials handling
   - Consent denial management
   - Token refresh failures
   - Fallback to password auth

3. **Quota Exceeded**
   - Prevent over-allocation
   - Alert administrators
   - Suggest alternatives

## Future Enhancements (Out of Current Scope)

- Microsoft 365 OAuth support
- Automated mailbox rotation
- Smart quota adjustment
- Mailbox health monitoring
- Automated credential testing
- Multi-factor authentication

---

**Version**: 1.0.0  
**Status**: Final  
**Last Updated**: July 2024