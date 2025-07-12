# Warmup Engine Module - API Reference

## Interface Class: WarmupEngineInterface

### Overview
The Warmup Engine Interface provides controlled access to warmup functionality for other modules. It manages warmup execution, monitoring, and configuration while ensuring quota compliance and maintaining sender reputation.

### Import
```python
from modules.warmup_engine.interface import WarmupEngineInterface

# Initialize
warmup_interface = WarmupEngineInterface()
```

## Warmup Status Methods

### get_warmup_status(mailbox_id: int) -> Dict[str, Any]
Get comprehensive warmup status for a mailbox.

**Parameters:**
- `mailbox_id` (int): Unique identifier of the mailbox

**Returns:**
```python
{
    'mailbox_id': 1,
    'email': 'john@example.com',
    'warmup_enabled': True,
    'warmup_day': 15,
    'plan_name': 'Standard 30-day',
    'status': 'active',  # active/paused/completed
    'today_target': 35,
    'today_sent': 28,
    'today_remaining': 7,
    'success_rate': 98.5,
    'last_send': '2024-07-11T14:30:00Z',
    'next_scheduled': '2024-07-11T15:00:00Z',
    'pause_reason': None,  # if paused
    'health_score': 95  # 0-100
}
```

**Exceptions:**
- `MailboxNotFoundError`: If mailbox doesn't exist
- `WarmupNotEnabledError`: If warmup not active

---

### pause_warmup(mailbox_id: int, reason: str) -> bool
Temporarily pause warmup for a mailbox.

**Parameters:**
- `mailbox_id` (int): Mailbox to pause
- `reason` (str): Explanation for pause

**Returns:**
- `True` if successfully paused
- `False` if already paused or not enabled

**Example:**
```python
if warmup_interface.pause_warmup(1, "Quota exceeded"):
    print("Warmup paused successfully")
```

**Events Emitted:**
- `warmup.paused` with pause reason

---

### resume_warmup(mailbox_id: int) -> bool
Resume paused warmup for a mailbox.

**Parameters:**
- `mailbox_id` (int): Mailbox to resume

**Returns:**
- `True` if successfully resumed
- `False` if not paused or not enabled

**Behavior:**
- Continues from same warmup day
- Recalculates remaining daily sends
- Updates schedule immediately

---

### get_warmup_stats(mailbox_id: int, days: int = 7) -> Dict[str, Any]
Retrieve historical warmup statistics.

**Parameters:**
- `mailbox_id` (int): Mailbox identifier
- `days` (int): Number of days to retrieve (default 7, max 30)

**Returns:**
```python
{
    'mailbox_id': 1,
    'period_days': 7,
    'stats': [
        {
            'date': '2024-07-11',
            'warmup_day': 15,
            'target_sends': 35,
            'actual_sends': 35,
            'internal_sends': 28,
            'external_sends': 7,
            'replies_received': 12,
            'bounces': 0,
            'success_rate': 100.0
        },
        # ... more days
    ],
    'summary': {
        'total_sent': 210,
        'total_replies': 72,
        'avg_success_rate': 98.5,
        'total_bounces': 2
    }
}
```

**Use Case:** Progress monitoring, reporting

---

### force_warmup_run(mailbox_id: int) -> Dict[str, Any]
Manually trigger warmup execution for a mailbox.

**Parameters:**
- `mailbox_id` (int): Mailbox to process

**Returns:**
```python
{
    'executed': True,
    'emails_sent': 5,
    'errors': [],
    'next_scheduled': '2024-07-11T16:00:00Z',
    'daily_limit_reached': False
}
```

**Restrictions:**
- Admin only
- Respects daily quotas
- Rate limited to prevent abuse

**Use Case:** Testing, manual intervention

---

### get_warmup_schedule(mailbox_id: int) -> List[Dict[str, Any]]
Get upcoming warmup schedule for today.

**Parameters:**
- `mailbox_id` (int): Mailbox identifier

**Returns:**
```python
[
    {
        'scheduled_time': '2024-07-11T15:00:00Z',
        'recipient_email': 'recipient1@example.com',
        'conversation_id': 'conv_123',
        'is_reply': False,
        'is_external': False,
        'status': 'pending'  # pending/sent/failed
    },
    # ... more scheduled emails
]
```

**Use Case:** Schedule visualization, debugging

---

### update_warmup_plan(mailbox_id: int, plan_id: int) -> bool
Change warmup plan for a mailbox.

**Parameters:**
- `mailbox_id` (int): Mailbox to update
- `plan_id` (int): New plan identifier

**Returns:**
- `True` if successfully updated
- `False` if invalid plan or mailbox

**Behavior:**
- Takes effect next day
- Maintains current warmup day
- Adjusts targets to new plan

## Bulk Operations

### get_warmup_summary() -> Dict[str, Any]
Get system-wide warmup overview.

**Parameters:** None

**Returns:**
```python
{
    'total_mailboxes': 150,
    'active_warmups': 120,
    'paused_warmups': 10,
    'completed_warmups': 20,
    'todays_target': 3500,
    'todays_sent': 2800,
    'todays_success_rate': 98.2,
    'issues': [
        {
            'mailbox_id': 5,
            'email': 'problem@example.com',
            'issue': 'High bounce rate',
            'severity': 'warning'
        }
    ]
}
```

**Use Case:** Dashboard, monitoring

---

### bulk_pause_warmup(mailbox_ids: List[int], reason: str) -> Dict[str, Any]
Pause multiple mailboxes simultaneously.

**Parameters:**
- `mailbox_ids` (List[int]): Mailboxes to pause
- `reason` (str): Common pause reason

**Returns:**
```python
{
    'requested': 10,
    'paused': 8,
    'already_paused': 1,
    'not_enabled': 1,
    'failed': 0
}
```

**Limits:** Maximum 100 mailboxes per call

## Configuration Methods

### get_available_plans() -> List[Dict[str, Any]]
List all configured warmup plans.

**Parameters:** None

**Returns:**
```python
[
    {
        'id': 1,
        'name': 'Standard 30-day',
        'description': 'Default progressive warmup',
        'is_default': True,
        'max_daily_volume': 300,
        'total_days': 30
    },
    {
        'id': 2,
        'name': 'Conservative 45-day',
        'description': 'Slower, safer warmup',
        'is_default': False,
        'max_daily_volume': 300,
        'total_days': 45
    }
]
```

---

### get_warmup_pairs(mailbox_id: int) -> List[Dict[str, Any]]
Get active pairs for a mailbox.

**Parameters:**
- `mailbox_id` (int): Mailbox identifier

**Returns:**
```python
[
    {
        'pair_id': 1,
        'partner_email': 'partner@example.com',
        'is_external': False,
        'pair_health': 98,
        'total_interactions': 45,
        'last_interaction': '2024-07-11T10:00:00Z',
        'status': 'active'
    },
    # ... more pairs
]
```

## Event Subscriptions

### Available Events

Other modules can subscribe to warmup events:

```python
from shared.events import subscribe

@subscribe('warmup.daily_complete')
def handle_daily_complete(event_data):
    mailbox_id = event_data['mailbox_id']
    emails_sent = event_data['emails_sent']
    # Update tracking, reports, etc.
```

**Events:**
- `warmup.started` - Warmup activated
- `warmup.paused` - Temporarily stopped
- `warmup.resumed` - Reactivated
- `warmup.completed` - 30-day plan finished
- `warmup.daily_complete` - Daily target reached
- `warmup.email_sent` - Individual email sent
- `warmup.email_failed` - Send failure
- `warmup.anomaly_detected` - Unusual pattern

**Event Data Format:**
```python
{
    'mailbox_id': 1,
    'email': 'john@example.com',
    'timestamp': '2024-07-11T15:30:00Z',
    'details': {
        # Event-specific data
    }
}
```

## Error Handling

### Exception Hierarchy
```
WarmupEngineError (base)
├── MailboxNotFoundError
├── WarmupNotEnabledError
├── QuotaExceededError
├── PlanNotFoundError
├── PairGenerationError
├── SchedulingError
└── ExecutionError
    ├── AuthenticationError
    ├── ConnectionError
    └── ContentGenerationError
```

### Example Error Handling
```python
from modules.warmup_engine.exceptions import (
    WarmupNotEnabledError,
    QuotaExceededError
)

try:
    status = warmup_interface.get_warmup_status(1)
except WarmupNotEnabledError:
    # Enable warmup first
    pass
except QuotaExceededError:
    # Handle quota issue
    warmup_interface.pause_warmup(1, "Quota exceeded")
```

## Rate Limits

To ensure system stability:

- `force_warmup_run`: Max 10 calls/hour per mailbox
- `get_warmup_status`: Max 1000 calls/minute
- `bulk_pause_warmup`: Max 10 calls/minute
- Schedule queries: Max 100 calls/minute

## Best Practices

1. **Monitor warmup health regularly**
   ```python
   status = warmup_interface.get_warmup_status(mailbox_id)
   if status['health_score'] < 80:
       # Investigate issues
       stats = warmup_interface.get_warmup_stats(mailbox_id)
   ```

2. **Handle quota limits gracefully**
   ```python
   status = warmup_interface.get_warmup_status(mailbox_id)
   if status['today_remaining'] == 0:
       # Daily limit reached, wait for tomorrow
       pass
   ```

3. **Use bulk operations for efficiency**
   ```python
   # Good: Single bulk call
   result = warmup_interface.bulk_pause_warmup([1, 2, 3], "Maintenance")
   
   # Bad: Multiple individual calls
   for id in [1, 2, 3]:
       warmup_interface.pause_warmup(id, "Maintenance")
   ```

4. **Subscribe to events for real-time updates**
   ```python
   @subscribe('warmup.anomaly_detected')
   def handle_anomaly(data):
       # Immediate response to issues
       logger.warning(f"Warmup anomaly: {data['details']}")
   ```

5. **Check prerequisites before operations**
   ```python
   # Verify warmup is enabled before getting stats
   try:
       stats = warmup_interface.get_warmup_stats(mailbox_id)
   except WarmupNotEnabledError:
       # Handle gracefully
       return None
   ```

---

**Version**: 1.0.0  
**Interface Stability**: Stable  
**Last Updated**: July 2024