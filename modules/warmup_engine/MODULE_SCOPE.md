# Warmup Engine Module - Scope Definition

## Module Purpose
The Warmup Engine module is responsible for executing automated email warmup campaigns between mailboxes to build sender reputation. It implements intelligent scheduling, pairing algorithms, and gradual volume increases following a 30-day warmup plan.

## Core Responsibilities

### 1. Warmup Planning and Scheduling
- Generate daily warmup plans based on mailbox age
- Schedule sends throughout the day (human-like patterns)
- Implement 30-day gradual volume increase
- Handle timezone-aware scheduling
- Manage warmup pause/resume functionality

### 2. Mailbox Pairing and Rotation
- Intelligent pairing to avoid same-domain sends
- External provider inclusion (20% ratio)
- Round-robin rotation for even distribution
- Pair health monitoring
- Dynamic re-pairing on failures

### 3. Email Generation and Sending
- Generate natural conversation threads
- Create contextual subject lines
- Personalized email bodies
- Reply chain management
- Attachment simulation (occasional)

### 4. Response Processing
- Monitor for warmup replies
- Process bounce notifications
- Track delivery success rates
- Handle auto-replies appropriately
- Update conversation threads

### 5. Statistics and Progress Tracking
- Track daily send volumes
- Monitor success/failure rates
- Calculate warmup progress
- Generate warmup reports
- Alert on anomalies

## Module Boundaries

### What This Module OWNS:
- `warmup_plans` database table
- `warmup_pairs` database table
- `warmup_conversations` database table
- `warmup_stats_daily` database table
- `warmup_email_log` database table
- Warmup execution logic
- Email content generation
- Scheduling algorithms

### What This Module DOES NOT Handle:
- Mailbox creation (Mailbox Management module)
- Server connections (VPS Management module)
- Credential storage (Mailbox Management module)
- Campaign emails (Campaign System module)
- General reporting (Reporting module)
- OAuth token refresh (Mailbox Management module)

## Data Models

### Warmup Plan Model
```
- id: Primary key
- name: Plan name (e.g., "Standard 30-day")
- schedule_json: Daily volume schedule
- internal_ratio: Internal vs external ratio
- reply_probability: Chance of generating reply
- peak_hours: Preferred sending hours
- is_default: Boolean flag
- created_at: Timestamp
- updated_at: Timestamp
```

### Warmup Pair Model
```
- id: Primary key
- sender_mailbox_id: Foreign key to mailboxes
- recipient_mailbox_id: Foreign key to mailboxes
- is_external: Boolean (external provider)
- pair_health: Score 0-100
- last_interaction: Timestamp
- total_interactions: Count
- status: active/paused/failed
- created_at: Timestamp
```

### Warmup Conversation Model
```
- id: Primary key
- thread_id: Unique conversation identifier
- sender_mailbox_id: Foreign key
- recipient_mailbox_id: Foreign key
- subject: Email subject line
- message_count: Number in thread
- last_message_at: Timestamp
- conversation_topic: Context/topic
- status: active/completed
- created_at: Timestamp
```

### Warmup Stats Daily Model
```
- id: Primary key
- mailbox_id: Foreign key to mailboxes
- date: Date of stats
- warmup_day: Day number in plan (1-30)
- target_sends: Planned sends
- actual_sends: Completed sends
- internal_sends: To other warmup mailboxes
- external_sends: To external providers
- replies_received: Reply count
- bounces: Bounce count
- success_rate: Percentage
- created_at: Timestamp
```

## Interface Methods

### Public API (for other modules)
```python
class WarmupEngineInterface:
    def get_warmup_status(mailbox_id: int) -> Dict
    def pause_warmup(mailbox_id: int, reason: str) -> bool
    def resume_warmup(mailbox_id: int) -> bool
    def get_warmup_stats(mailbox_id: int, days: int = 7) -> Dict
    def force_warmup_run(mailbox_id: int) -> Dict
    def get_warmup_schedule(mailbox_id: int) -> List[Dict]
    def update_warmup_plan(mailbox_id: int, plan_id: int) -> bool
```

### Events Emitted
- `warmup.started` - Warmup activated for mailbox
- `warmup.paused` - Warmup temporarily stopped
- `warmup.resumed` - Warmup reactivated
- `warmup.completed` - 30-day plan finished
- `warmup.daily_complete` - Daily quota reached
- `warmup.email_sent` - Individual email sent
- `warmup.email_failed` - Send failure
- `warmup.anomaly_detected` - Unusual pattern detected

### Events Subscribed To
- `mailbox.created` - Initialize warmup if enabled
- `mailbox.deleted` - Clean up warmup data
- `mailbox.warmup_enabled` - Start warmup process
- `mailbox.warmup_disabled` - Stop warmup process
- `server.status_changed` - Pause affected mailboxes

## Security Requirements

1. **Email Content Security**
   - No sensitive data in warmup emails
   - Randomized but safe content
   - No links to external sites
   - No executable attachments

2. **Rate Limiting**
   - Respect daily quotas strictly
   - Implement send delays
   - Prevent quota bypass attempts
   - Honor provider limits

3. **Access Control**
   - Only system can execute warmup
   - Read-only access to stats
   - Admin-only configuration changes
   - Audit all manual interventions

## Performance Requirements

- Email generation: < 50ms per email
- Scheduling calculation: < 1s per mailbox
- Bulk operations: Process 1000 mailboxes/minute
- Response processing: < 100ms per email
- Stats aggregation: < 5s for monthly data

## Dependencies

### On Core Foundation:
- Database service for persistence
- Task scheduler for automation
- Logging service for tracking
- Event bus for notifications

### On Mailbox Management:
- Mailbox availability checks
- Credential retrieval
- Quota verification
- OAuth token access

### On VPS Management:
- Server connection management
- Server availability checks
- Connection pooling

### External Dependencies:
- Email parsing libraries
- Natural language generation
- SMTP/IMAP clients
- Template engines

## Error Handling

1. **Send Failures**
   - Retry with exponential backoff
   - Mark pair as unhealthy after repeated failures
   - Find alternative recipient
   - Log detailed error info

2. **Quota Exceeded**
   - Stop sending immediately
   - Mark daily quota as reached
   - Resume next day automatically
   - Alert if pattern continues

3. **Authentication Failures**
   - Pause mailbox warmup
   - Emit authentication error event
   - Retry after credential update
   - Skip mailbox if persistent

## Warmup Algorithm

### 30-Day Progressive Schedule
```
Day 1-3:   2-5 emails/day
Day 4-7:   5-10 emails/day
Day 8-14:  10-25 emails/day
Day 15-21: 25-50 emails/day
Day 22-28: 50-150 emails/day
Day 29-30: 150-300 emails/day
```

### Inactivity Reset
- If no activity for 30+ days, reset to Day 1
- Gradual ramp-up prevents reputation damage
- Track last activity date
- Automatic detection and reset

## Future Enhancements (Out of Current Scope)

- AI-powered content generation
- Sentiment analysis for responses
- Advanced scheduling optimization
- Multi-language support
- Industry-specific templates
- Reputation score prediction
- A/B testing warmup strategies

---

**Version**: 1.0.0  
**Status**: Final  
**Last Updated**: July 2024