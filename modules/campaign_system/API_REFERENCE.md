# Campaign System Module - API Reference

## Interface Class: CampaignSystemInterface

### Overview
The Campaign System Interface provides controlled access to campaign functionality for other modules. It manages campaign lifecycle, recipient handling, and delivery coordination while ensuring compliance and quota management.

### Import
```python
from modules.campaign_system.interface import CampaignSystemInterface

# Initialize
campaign_interface = CampaignSystemInterface()
```

## Campaign Information Methods

### get_campaign_info(campaign_id: int) -> Dict[str, Any]
Retrieve detailed information about a specific campaign.

**Parameters:**
- `campaign_id` (int): Unique identifier of the campaign

**Returns:**
```python
{
    'id': 1,
    'name': 'Summer Newsletter',
    'subject': 'Summer Sale - 50% Off!',
    'from_name': 'Acme Sales',
    'reply_to': 'sales@acme.com',
    'status': 'active',  # draft/scheduled/active/paused/completed
    'scheduled_at': '2024-07-15T09:00:00Z',
    'started_at': '2024-07-15T09:00:00Z',
    'completed_at': None,
    'throttle_per_hour': 5000,
    'total_recipients': 50000,
    'sent_count': 25000,
    'queued_count': 5000,
    'failed_count': 100,
    'open_rate': 24.5,
    'click_rate': 3.2,
    'bounce_rate': 0.5,
    'unsubscribe_rate': 0.1,
    'created_by': 'admin@acme.com',
    'created_at': '2024-07-10T14:30:00Z'
}
```

**Exceptions:**
- `CampaignNotFoundError`: If campaign_id doesn't exist
- `PermissionError`: If caller lacks read permission

---

### get_active_campaigns() -> List[Dict[str, Any]]
Get all currently active campaigns.

**Parameters:** None

**Returns:**
```python
[
    {
        'id': 1,
        'name': 'Summer Newsletter',
        'status': 'active',
        'progress_percentage': 50.0,
        'sent_count': 25000,
        'total_recipients': 50000,
        'send_rate': 4500,  # per hour
        'estimated_completion': '2024-07-15T15:30:00Z'
    },
    # ... more campaigns
]
```

**Use Case:** System monitoring, resource allocation

---

### get_mailbox_campaigns(mailbox_id: int) -> List[Dict[str, Any]]
Get campaigns using a specific mailbox.

**Parameters:**
- `mailbox_id` (int): Mailbox identifier

**Returns:**
```python
[
    {
        'campaign_id': 1,
        'campaign_name': 'Summer Newsletter',
        'assigned_recipients': 5000,
        'sent_count': 2500,
        'daily_limit': 300,
        'send_rate': 250,  # current rate
        'is_active': True,
        'last_sent_at': '2024-07-11T14:45:00Z'
    },
    # ... more campaigns
]
```

**Use Case:** Quota coordination with warmup

---

### get_campaign_stats(campaign_id: int) -> Dict[str, Any]
Get detailed campaign statistics.

**Parameters:**
- `campaign_id` (int): Campaign identifier

**Returns:**
```python
{
    'campaign_id': 1,
    'delivery_stats': {
        'sent': 25000,
        'delivered': 24800,
        'bounced': 125,
        'failed': 75,
        'pending': 25000
    },
    'engagement_stats': {
        'unique_opens': 6125,
        'total_opens': 8500,
        'unique_clicks': 800,
        'total_clicks': 1200,
        'replies': 45,
        'unsubscribes': 25
    },
    'bounce_breakdown': {
        'soft_bounces': 100,
        'hard_bounces': 25
    },
    'device_stats': {
        'desktop': 45.5,
        'mobile': 48.2,
        'tablet': 6.3
    },
    'top_links': [
        {'url': 'https://acme.com/sale', 'clicks': 450},
        {'url': 'https://acme.com/products', 'clicks': 300}
    ]
}
```

---

## Campaign Control Methods

### pause_campaign(campaign_id: int, reason: str) -> bool
Temporarily pause an active campaign.

**Parameters:**
- `campaign_id` (int): Campaign to pause
- `reason` (str): Explanation for pause

**Returns:**
- `True` if successfully paused
- `False` if not active or already paused

**Example:**
```python
if campaign_interface.pause_campaign(1, "Quota exceeded"):
    print("Campaign paused successfully")
```

**Events Emitted:**
- `campaign.paused` with pause reason

---

### resume_campaign(campaign_id: int) -> bool
Resume a paused campaign.

**Parameters:**
- `campaign_id` (int): Campaign to resume

**Returns:**
- `True` if successfully resumed
- `False` if not paused

**Behavior:**
- Recalculates sending schedule
- Respects current quotas
- Updates estimated completion

---

### cancel_campaign(campaign_id: int) -> bool
Permanently stop a campaign.

**Parameters:**
- `campaign_id` (int): Campaign to cancel

**Returns:**
- `True` if cancelled
- `False` if already completed

**Warning:** This action cannot be undone

---

## Recipient Management Methods

### check_recipient_status(email: str) -> Dict[str, Any]
Check if an email can receive campaigns.

**Parameters:**
- `email` (str): Email address to check

**Returns:**
```python
{
    'email': 'john@example.com',
    'can_receive': False,
    'reasons': ['global_suppression', 'hard_bounce'],
    'suppression_date': '2024-06-15T10:30:00Z',
    'last_campaign': {
        'id': 5,
        'name': 'June Newsletter',
        'sent_at': '2024-06-10T09:00:00Z',
        'status': 'bounced'
    },
    'engagement_score': 0,
    'total_received': 10,
    'total_opened': 0,
    'total_clicked': 0
}
```

**Use Case:** Pre-send validation

---

### add_to_suppression(email: str, reason: str) -> bool
Add email to global suppression list.

**Parameters:**
- `email` (str): Email to suppress
- `reason` (str): Suppression reason

**Returns:**
- `True` if added successfully
- `False` if already suppressed

**Valid Reasons:**
- `manual` - Admin addition
- `unsubscribe` - User opt-out
- `bounce` - Delivery failure
- `complaint` - Spam complaint
- `invalid` - Invalid address

---

### remove_from_suppression(email: str) -> bool
Remove email from suppression list.

**Parameters:**
- `email` (str): Email to unsuppress

**Returns:**
- `True` if removed
- `False` if not suppressed

**Note:** Requires admin permission

---

## Quota and Resource Methods

### get_campaign_quota_usage(campaign_id: int) -> Dict[str, Any]
Get current quota usage for campaign.

**Parameters:**
- `campaign_id` (int): Campaign identifier

**Returns:**
```python
{
    'campaign_id': 1,
    'mailboxes': [
        {
            'mailbox_id': 1,
            'email': 'sender1@acme.com',
            'daily_quota': 300,
            'used_today': 250,
            'campaign_used': 200,
            'available': 50,
            'next_reset': '2024-07-12T00:00:00Z'
        },
        # ... more mailboxes
    ],
    'total_available': 500,
    'send_rate': 4500,  # per hour
    'throttle_active': False
}
```

---

### allocate_campaign_quotas(campaign_id: int, allocations: Dict[int, int]) -> bool
Manually allocate quotas to mailboxes.

**Parameters:**
- `campaign_id` (int): Campaign identifier
- `allocations` (Dict[int, int]): {mailbox_id: daily_limit}

**Returns:**
- `True` if allocated successfully
- `False` if invalid allocations

**Example:**
```python
allocations = {
    1: 200,  # Mailbox 1 gets 200/day
    2: 150,  # Mailbox 2 gets 150/day
    3: 300   # Mailbox 3 gets 300/day
}
campaign_interface.allocate_campaign_quotas(1, allocations)
```

---

## Bulk Operations

### get_campaigns_summary(status: str = None) -> Dict[str, Any]
Get summary of all campaigns.

**Parameters:**
- `status` (str, optional): Filter by status

**Returns:**
```python
{
    'total_campaigns': 150,
    'by_status': {
        'draft': 20,
        'scheduled': 5,
        'active': 3,
        'paused': 2,
        'completed': 120
    },
    'active_recipients': 75000,
    'emails_per_hour': 13500,
    'next_scheduled': {
        'campaign_id': 10,
        'name': 'Weekend Special',
        'scheduled_at': '2024-07-13T10:00:00Z'
    }
}
```

---

## Event Subscriptions

### Available Events

Other modules can subscribe to campaign events:

```python
from shared.events import subscribe

@subscribe('campaign.email_sent')
def track_send(event_data):
    campaign_id = event_data['campaign_id']
    recipient_id = event_data['recipient_id']
    mailbox_id = event_data['mailbox_id']
    # Update tracking
```

**Events:**
- `campaign.created` - New campaign
- `campaign.started` - Sending begins
- `campaign.paused` - Temporarily stopped
- `campaign.resumed` - Restarted
- `campaign.completed` - Finished
- `campaign.email_sent` - Individual send
- `campaign.email_opened` - Open tracked
- `campaign.email_clicked` - Click tracked
- `campaign.email_bounced` - Bounce received
- `campaign.unsubscribe` - Opt-out

**Event Data Format:**
```python
{
    'campaign_id': 1,
    'timestamp': '2024-07-11T15:30:00Z',
    'details': {
        # Event-specific data
    }
}
```

## Error Handling

### Exception Hierarchy
```
CampaignSystemError (base)
├── CampaignNotFoundError
├── RecipientError
│   ├── InvalidEmailError
│   ├── SuppressionError
│   └── DuplicateRecipientError
├── TemplateError
├── QuotaError
│   ├── InsufficientQuotaError
│   └── QuotaAllocationError
├── SendingError
│   ├── MailboxUnavailableError
│   └── DeliveryError
└── ValidationError
```

### Example Error Handling
```python
from modules.campaign_system.exceptions import (
    CampaignNotFoundError,
    InsufficientQuotaError
)

try:
    campaign_interface.resume_campaign(1)
except CampaignNotFoundError:
    print("Campaign not found")
except InsufficientQuotaError as e:
    print(f"Not enough quota: {e.available} < {e.required}")
```

## Rate Limits

To ensure system stability:

- `get_campaign_info`: Max 1000 calls/minute
- `pause/resume_campaign`: Max 60 calls/minute
- `check_recipient_status`: Max 10000 calls/minute
- `add_to_suppression`: Max 1000 calls/minute
- Stats queries: Max 100 calls/minute

## Best Practices

1. **Check quotas before resuming**
   ```python
   quota = campaign_interface.get_campaign_quota_usage(campaign_id)
   if quota['total_available'] > 1000:
       campaign_interface.resume_campaign(campaign_id)
   ```

2. **Validate recipients before campaigns**
   ```python
   status = campaign_interface.check_recipient_status(email)
   if not status['can_receive']:
       # Handle suppressed recipient
       logger.info(f"Skipping {email}: {status['reasons']}")
   ```

3. **Monitor campaign progress**
   ```python
   @subscribe('campaign.email_sent')
   def monitor_progress(data):
       if data['sent_count'] % 1000 == 0:
           stats = campaign_interface.get_campaign_stats(data['campaign_id'])
           logger.info(f"Progress: {stats['delivery_stats']['sent']}")
   ```

4. **Handle quota exhaustion gracefully**
   ```python
   @subscribe('mailbox.quota_exceeded')
   def handle_quota_exceeded(data):
       # Find campaigns using this mailbox
       campaigns = campaign_interface.get_mailbox_campaigns(data['mailbox_id'])
       for campaign in campaigns:
           if campaign['is_active']:
               campaign_interface.pause_campaign(
                   campaign['campaign_id'], 
                   f"Mailbox {data['mailbox_id']} quota exceeded"
               )
   ```

---

**Version**: 1.0.0  
**Interface Stability**: Stable  
**Last Updated**: July 2024