# Warmup Engine Module

## Quick Overview

The Warmup Engine module orchestrates automated email warmup campaigns to build sender reputation. It implements intelligent scheduling, natural conversation generation, and progressive volume increases following a proven 30-day warmup strategy.

## Key Responsibilities
- 📈 Execute 30-day progressive warmup plans
- 🤝 Manage intelligent mailbox pairing
- 💬 Generate natural email conversations
- ⏰ Human-like scheduling patterns
- 📊 Track warmup progress and health
- 🔄 Process replies and bounces

## Module Status
- **Version**: 1.0.0
- **Stability**: Stable
- **Dependencies**: Core Foundation, Mailbox Management, VPS Management
- **Required By**: Campaign System (for quota coordination)

## Quick Start

### For Module Users (Other Modules)
```python
from modules.warmup_engine.interface import WarmupEngineInterface

warmup = WarmupEngineInterface()

# Check warmup status
status = warmup.get_warmup_status(mailbox_id)
print(f"Day {status['warmup_day']}: {status['today_sent']}/{status['today_target']}")

# Pause if needed
if quota_issue:
    warmup.pause_warmup(mailbox_id, "Quota exceeded")

# Get statistics
stats = warmup.get_warmup_stats(mailbox_id, days=7)
```

### For Administrators

1. **View Status**: `/warmup/dashboard`
2. **Manage Plans**: `/warmup/plans`
3. **Monitor Progress**: `/warmup/progress`
4. **View Pairs**: `/warmup/pairs`

## Documentation

- 📋 [Module Scope](MODULE_SCOPE.md) - Detailed boundaries and responsibilities
- 🔧 [Features](FEATURES.md) - Complete feature list
- 📚 [API Reference](API_REFERENCE.md) - Interface documentation

## Database Tables

This module owns:
- `warmup_plans` - Warmup schedule configurations
- `warmup_pairs` - Sender-recipient relationships
- `warmup_conversations` - Email thread tracking
- `warmup_stats_daily` - Daily progress metrics
- `warmup_email_log` - Individual email records

## How Warmup Works

### 30-Day Progressive Schedule
```
Days 1-3:   2-5 emails/day     (Building foundation)
Days 4-7:   5-10 emails/day    (Establishing pattern)
Days 8-14:  10-25 emails/day   (Gradual increase)
Days 15-21: 25-50 emails/day   (Reputation building)
Days 22-28: 50-150 emails/day  (Volume scaling)
Days 29-30: 150-300 emails/day (Full capacity)
```

### Key Features
- **Smart Pairing**: Avoids same-domain sends
- **External Mix**: 20% to Gmail/Outlook/Yahoo
- **Natural Timing**: Business hours focus
- **Auto-replies**: 30-40% reply rate simulation
- **Inactivity Reset**: Returns to Day 1 after 30 days inactive

## Common Operations

### Check System Health
```python
summary = warmup.get_warmup_summary()
print(f"Active warmups: {summary['active_warmups']}")
print(f"Today's progress: {summary['todays_sent']}/{summary['todays_target']}")
```

### Force Warmup Run (Testing)
```python
result = warmup.force_warmup_run(mailbox_id)
if result['executed']:
    print(f"Sent {result['emails_sent']} emails")
```

### Monitor Specific Mailbox
```python
# Get detailed stats
stats = warmup.get_warmup_stats(mailbox_id, days=30)
for day in stats['stats']:
    print(f"{day['date']}: {day['actual_sends']}/{day['target_sends']}")
```

## Events

### Emitted Events
- `warmup.started`
- `warmup.paused`
- `warmup.resumed`
- `warmup.completed`
- `warmup.daily_complete`
- `warmup.email_sent`
- `warmup.anomaly_detected`

### Subscribe to Events
```python
from shared.events import subscribe

@subscribe('warmup.anomaly_detected')
def handle_anomaly(event_data):
    # Alert on unusual patterns
    mailbox_id = event_data['mailbox_id']
    issue = event_data['details']['issue']
    alert_admin(f"Warmup issue for {mailbox_id}: {issue}")
```

## Troubleshooting

### Low Success Rate
1. Check pair health scores
2. Verify mailbox credentials
3. Review bounce patterns
4. Check server connectivity

### Warmup Not Progressing
1. Verify warmup is enabled
2. Check for paused status
3. Review daily logs
4. Verify quota availability

### High Bounce Rate
1. Check recipient validity
2. Review server reputation
3. Verify DNS configuration
4. Consider slower progression

## Configuration

### Warmup Plans
- **Standard**: 30-day progressive (default)
- **Conservative**: 45-day slower build
- **Aggressive**: 21-day faster ramp

### External Providers
Default seedlist includes:
- Gmail addresses (33%)
- Outlook addresses (33%)
- Yahoo addresses (34%)

## Performance Notes

- Processes 1000+ mailboxes concurrently
- Generates unique content for every email
- Maintains conversation context
- Real-time response processing

## Support

- 📝 Log Location: `/var/log/warmup_engine/`
- 🐛 Report Issues: Create ticket with module tag
- 📧 Module Owner: Email Deliverability Team

---

For development and contribution guidelines, see the main [ARCHITECTURE.md](/root/ARCHITECTURE.md) document.