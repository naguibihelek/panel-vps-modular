# Campaign System Module

## Quick Overview

The Campaign System module manages email marketing campaigns from creation to completion. It handles recipient management, template processing, sending orchestration, and response tracking while ensuring compliance and respecting mailbox quotas.

## Key Responsibilities
- 📧 Create and manage email campaigns
- 👥 Import and segment recipients
- 📝 Process email templates with personalization
- 🚀 Orchestrate sending across mailboxes
- 📊 Track opens, clicks, and responses
- 🛡️ Ensure compliance (CAN-SPAM, GDPR)

## Module Status
- **Version**: 1.0.0
- **Stability**: Stable
- **Dependencies**: Core Foundation, Mailbox Management, VPS Management
- **Required By**: Reporting, Integrations

## Quick Start

### For Module Users (Other Modules)
```python
from modules.campaign_system.interface import CampaignSystemInterface

campaign = CampaignSystemInterface()

# Check active campaigns
active = campaign.get_active_campaigns()
for c in active:
    print(f"{c['name']}: {c['progress_percentage']}% complete")

# Pause campaign if quota issue
campaign.pause_campaign(campaign_id, "Quota exceeded")

# Check if email can receive campaigns
status = campaign.check_recipient_status('user@example.com')
```

### For Campaign Managers

1. **Create Campaign**: `/campaigns/create`
2. **Import Recipients**: `/campaigns/{id}/recipients`
3. **Design Template**: `/campaigns/{id}/template`
4. **Schedule Send**: `/campaigns/{id}/schedule`
5. **Monitor Progress**: `/campaigns/{id}/dashboard`

## Documentation

- 📋 [Module Scope](MODULE_SCOPE.md) - Detailed boundaries and responsibilities
- 🔧 [Features](FEATURES.md) - Complete feature list
- 📚 [API Reference](API_REFERENCE.md) - Interface documentation

## Database Tables

This module owns:
- `campaigns` - Campaign configurations
- `campaign_recipients` - Recipient lists and status
- `campaign_templates` - Email templates
- `campaign_mailboxes` - Mailbox assignments
- `campaign_emails` - Individual email records
- `campaign_events` - Tracking events

## Campaign Workflow

### 1. Campaign Setup
```python
# Create campaign
# Import recipients
# Select template
# Configure settings
```

### 2. Recipient Processing
- Import from CSV/API
- Validate email addresses
- Check suppression lists
- Apply segmentation

### 3. Sending Process
- Assign to mailboxes
- Respect quotas
- Apply throttling
- Queue for delivery

### 4. Response Tracking
- Monitor opens/clicks
- Process bounces
- Handle unsubscribes
- Calculate metrics

## Common Operations

### Check Campaign Status
```python
info = campaign.get_campaign_info(campaign_id)
print(f"Sent: {info['sent_count']}/{info['total_recipients']}")
print(f"Open Rate: {info['open_rate']}%")
```

### Monitor Quota Usage
```python
quota = campaign.get_campaign_quota_usage(campaign_id)
for mailbox in quota['mailboxes']:
    print(f"{mailbox['email']}: {mailbox['available']} available")
```

### Handle Suppression
```python
# Check before sending
if not campaign.check_recipient_status(email)['can_receive']:
    # Skip this recipient
    pass

# Add to suppression
campaign.add_to_suppression(email, 'unsubscribe')
```

## Events

### Emitted Events
- `campaign.created`
- `campaign.started`
- `campaign.paused`
- `campaign.completed`
- `campaign.email_sent`
- `campaign.email_opened`
- `campaign.email_clicked`
- `campaign.email_bounced`

### Subscribe to Events
```python
from shared.events import subscribe

@subscribe('campaign.email_bounced')
def handle_bounce(event_data):
    # Update recipient status
    # Clean mailing list
    pass
```

## Compliance Features

### CAN-SPAM Requirements
- ✅ Physical address in footer
- ✅ Clear sender identification
- ✅ One-click unsubscribe
- ✅ Accurate subject lines
- ✅ Opt-out processing within 10 days

### GDPR Compliance
- ✅ Consent tracking
- ✅ Data portability
- ✅ Right to deletion
- ✅ Processing records
- ✅ Preference center

## Performance Guidelines

- **Recipient Import**: 10,000/minute
- **Email Queueing**: 1,000/second
- **Concurrent Campaigns**: Unlimited
- **Real-time Tracking**: < 100ms
- **Stats Calculation**: < 5s for 1M recipients

## Troubleshooting

### Campaign Not Sending
1. Check campaign status (not paused)
2. Verify mailbox quotas available
3. Check recipient validation
4. Review error logs

### Low Open Rates
1. Check spam score
2. Review subject lines
3. Verify sender reputation
4. Check delivery timing

### Bounce Issues
1. Review bounce types
2. Clean email lists
3. Check DNS/SPF/DKIM
4. Monitor blacklists

## Best Practices

1. **Test Before Sending**
   - Send test emails
   - Check rendering
   - Verify links
   - Test personalizations

2. **Monitor Reputation**
   - Track bounce rates (< 2%)
   - Monitor complaints (< 0.1%)
   - Check blacklists
   - Review engagement

3. **Optimize Timing**
   - Send during business hours
   - Consider timezones
   - Avoid weekends
   - Test send times

## Support

- 📝 Log Location: `/var/log/campaign_system/`
- 🐛 Report Issues: Create ticket with module tag
- 📧 Module Owner: Marketing Operations Team

---

For development and contribution guidelines, see the main [ARCHITECTURE.md](/root/ARCHITECTURE.md) document.