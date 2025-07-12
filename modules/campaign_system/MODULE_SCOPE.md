# Campaign System Module - Scope Definition

## Module Purpose
The Campaign System module manages the creation, scheduling, and execution of email marketing campaigns. It handles campaign configuration, recipient management, template processing, and coordinates with the sending infrastructure while respecting quotas and delivery rules.

## Core Responsibilities

### 1. Campaign Management
- Create and configure email campaigns
- Define campaign metadata and settings
- Schedule campaign execution
- Manage campaign lifecycle (draft/active/paused/completed)
- Handle campaign cloning and templates

### 2. Recipient Management
- Import and validate recipient lists
- Manage recipient segments and tags
- Track recipient engagement status
- Handle unsubscribes and bounces
- Implement suppression lists

### 3. Email Template Processing
- Store and manage email templates
- Process merge variables and personalization
- Handle dynamic content insertion
- Manage template versions
- Support HTML and plain text formats

### 4. Sending Orchestration
- Queue emails for delivery
- Respect mailbox quotas
- Implement sending throttling
- Coordinate with warmup quotas
- Handle retry logic

### 5. Response Tracking
- Track email opens and clicks
- Monitor bounce rates
- Process unsubscribe requests
- Record reply detection
- Generate campaign metrics

## Module Boundaries

### What This Module OWNS:
- `campaigns` database table
- `campaign_recipients` database table
- `campaign_templates` database table
- `campaign_mailboxes` database table
- `campaign_emails` database table
- `campaign_events` database table
- Campaign creation and configuration
- Recipient list management
- Email queueing logic

### What This Module DOES NOT Handle:
- Actual email sending (uses Mailbox Management)
- Server connections (VPS Management)
- Warmup execution (Warmup Engine)
- Detailed analytics (Reporting module)
- Webhook processing (Integrations module)
- Mailbox credentials (Mailbox Management)

## Data Models

### Campaign Model
```
- id: Primary key
- name: Campaign name
- subject: Email subject line
- from_name: Sender display name
- reply_to: Reply-to address
- template_id: Foreign key to templates
- status: draft/scheduled/active/paused/completed
- scheduled_at: When to start sending
- throttle_per_hour: Max emails per hour
- total_recipients: Recipient count
- sent_count: Emails sent
- open_rate: Percentage opened
- click_rate: Percentage clicked
- bounce_rate: Percentage bounced
- created_by: User who created
- created_at: Timestamp
- updated_at: Timestamp
```

### Campaign Recipient Model
```
- id: Primary key
- campaign_id: Foreign key to campaigns
- email: Recipient email address
- first_name: Recipient first name
- last_name: Recipient last name
- company: Recipient company
- custom_fields: JSON for extra data
- tags: JSON array of tags
- status: pending/sent/opened/clicked/bounced/unsubscribed
- sent_at: When email was sent
- opened_at: First open timestamp
- clicked_at: First click timestamp
- bounced_at: Bounce timestamp
- unsubscribed_at: Unsubscribe timestamp
```

### Campaign Template Model
```
- id: Primary key
- name: Template name
- html_content: HTML version
- text_content: Plain text version
- merge_tags: JSON array of available tags
- preview_text: Email preview text
- category: Template category
- is_active: Boolean flag
- created_by: Creator user
- created_at: Timestamp
- updated_at: Timestamp
```

### Campaign Mailbox Model
```
- id: Primary key
- campaign_id: Foreign key to campaigns
- mailbox_id: Foreign key to mailboxes
- assigned_recipients: Number assigned
- sent_count: Emails sent via this mailbox
- daily_limit: Max per day for campaign
- is_active: Currently sending
- last_sent_at: Last email timestamp
```

### Campaign Email Model
```
- id: Primary key
- campaign_id: Foreign key to campaigns
- recipient_id: Foreign key to recipients
- mailbox_id: Sending mailbox
- message_id: Email message ID
- status: queued/sent/failed/bounced
- attempts: Send attempt count
- sent_at: Successful send time
- error_message: If failed
- tracking_id: For open/click tracking
```

## Interface Methods

### Public API (for other modules)
```python
class CampaignSystemInterface:
    def get_campaign_info(campaign_id: int) -> Dict
    def get_active_campaigns() -> List[Dict]
    def get_mailbox_campaigns(mailbox_id: int) -> List[Dict]
    def pause_campaign(campaign_id: int, reason: str) -> bool
    def resume_campaign(campaign_id: int) -> bool
    def get_campaign_stats(campaign_id: int) -> Dict
    def check_recipient_status(email: str) -> Dict
    def add_to_suppression(email: str, reason: str) -> bool
```

### Events Emitted
- `campaign.created` - New campaign created
- `campaign.started` - Campaign begins sending
- `campaign.paused` - Campaign paused
- `campaign.resumed` - Campaign resumed
- `campaign.completed` - All emails sent
- `campaign.email_sent` - Individual email sent
- `campaign.email_opened` - Email opened
- `campaign.email_clicked` - Link clicked
- `campaign.email_bounced` - Email bounced
- `campaign.unsubscribe` - Recipient unsubscribed

### Events Subscribed To
- `mailbox.quota_exceeded` - Pause affected campaigns
- `mailbox.deleted` - Reassign campaign emails
- `warmup.daily_complete` - Adjust campaign sending

## Security Requirements

1. **Data Protection**
   - Encrypt sensitive recipient data
   - Secure template storage
   - Protected tracking pixels
   - Safe unsubscribe links

2. **Access Control**
   - Role-based campaign access
   - Template approval workflow
   - Recipient list permissions
   - Campaign modification audit

3. **Compliance**
   - CAN-SPAM compliance
   - GDPR compliance features
   - Unsubscribe handling
   - Data retention policies

## Performance Requirements

- Campaign creation: < 2s
- Recipient import: 10,000 recipients/minute
- Email queueing: 1,000 emails/second
- Stats calculation: < 5s for 1M recipients
- Real-time tracking: < 100ms response

## Dependencies

### On Core Foundation:
- Database service for persistence
- Authentication for access control
- Event bus for notifications
- Task scheduler for sending

### On Mailbox Management:
- Mailbox availability
- Credential access
- Quota checking
- Send capability

### On VPS Management:
- Server availability
- Connection management

### External Dependencies:
- CSV parsing libraries
- HTML sanitization
- Email validation
- Template engines
- Tracking pixel generation

## Error Handling

1. **Send Failures**
   - Automatic retry logic
   - Exponential backoff
   - Failure notifications
   - Alternative mailbox selection

2. **Quota Management**
   - Real-time quota tracking
   - Automatic throttling
   - Campaign pausing
   - Fair distribution

3. **Bounce Processing**
   - Soft vs hard bounce detection
   - Automatic list cleaning
   - Reputation protection
   - Suppression list updates

## Campaign Execution Flow

1. **Campaign Creation**
   - Define settings and template
   - Import recipient list
   - Assign mailboxes
   - Schedule or start

2. **Email Processing**
   - Load recipient batch
   - Apply personalizations
   - Check suppressions
   - Queue for sending

3. **Delivery Management**
   - Respect quotas
   - Track attempts
   - Handle responses
   - Update statistics

## Future Enhancements (Out of Current Scope)

- A/B testing capabilities
- Advanced segmentation
- Behavioral triggers
- Multi-step campaigns
- SMS integration
- Push notification campaigns
- Advanced personalization AI

---

**Version**: 1.0.0  
**Status**: Final  
**Last Updated**: July 2024