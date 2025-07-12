# Module Boundaries and Interaction Rules

## Purpose
This document defines the STRICT boundaries between modules and the ONLY permitted ways modules can interact. Violating these boundaries will break the system architecture and is FORBIDDEN.

## Module Boundary Definitions

### What IS a Module Boundary?
A module boundary is the line between what a module owns and controls versus what belongs to other modules or core. Think of each module as a locked room - you can only interact through the door (interface), not by breaking through walls.

### Boundary Violations (FORBIDDEN)
```python
# ❌ NEVER DO THIS - Direct import from another module
from modules.warmup_engine.services.planner import WarmupPlanner

# ❌ NEVER DO THIS - Accessing another module's database tables
db.query("SELECT * FROM campaign_recipients")  # Only Campaign System can access this

# ❌ NEVER DO THIS - Reaching into another module's files
config = json.load(open("modules/vps_management/config.json"))
```

### Correct Interactions (REQUIRED)
```python
# ✅ DO THIS - Use the module interface
from shared.interfaces import WarmupInterface
warmup = WarmupInterface()
quota = warmup.get_mailbox_quota(mailbox_id)

# ✅ DO THIS - Subscribe to events
from shared.events import subscribe
subscribe('mailbox.created', handle_new_mailbox)

# ✅ DO THIS - Request data through Core
from core.database import DatabaseService
db = DatabaseService()
data = db.get_mailbox_data(mailbox_id)  # Core handles the query
```

## Module Ownership Map

### VPS Management Module OWNS:
**Database Tables:**
- servers (server configurations)
- domains (domain settings)
- dns_records (DNS configurations)

**Operations:**
- Create/update/delete servers
- Manage server credentials
- Configure domains and DNS
- Monitor server connectivity

**CANNOT:**
- Create mailboxes (must call MailboxInterface)
- Send emails (must call WarmupInterface or CampaignInterface)
- Access campaign data

---

### Mailbox Management Module OWNS:
**Database Tables:**
- mailboxes (account details)
- password_groups (shared passwords)
- oauth_configs (OAuth settings)

**Operations:**
- Create/delete mailboxes
- Update credentials
- Manage OAuth flows
- Bulk import operations

**CANNOT:**
- Send emails directly
- Modify warmup schedules
- Access server internals

---

### Warmup Engine Module OWNS:
**Database Tables:**
- warmup_stats_daily (send statistics)
- warmup_targets (ramp schedule)
- warmup_conversations (thread tracking)
- warmup_plans (daily plans)

**Operations:**
- Schedule warmup sends
- Execute warmup emails
- Track warmup progress
- Manage quotas

**CANNOT:**
- Create/delete mailboxes
- Send campaign emails
- Modify server settings

---

### Campaign System Module OWNS:
**Database Tables:**
- campaigns (campaign definitions)
- campaign_recipients (recipient lists)
- campaign_mailboxes (sender assignments)
- campaign_stats (performance data)

**Operations:**
- Create/edit campaigns
- Upload recipients
- Schedule sends
- Track results

**CANNOT:**
- Modify warmup logic
- Create mailboxes
- Access server credentials

---

### Reporting Module OWNS:
**Database Tables:**
- None (read-only module)

**Operations:**
- Generate statistics
- Create visualizations
- Export reports
- Monitor resources

**CANNOT:**
- Modify any data
- Send emails
- Change configurations

---

### Integrations Module OWNS:
**Database Tables:**
- webhook_configs (webhook settings)
- integration_logs (processing logs)
- response_rules (classification rules)

**Operations:**
- Process responses
- Call webhooks
- Forward to external systems
- OAuth token management

**CANNOT:**
- Send emails directly
- Modify mailbox settings
- Change warmup plans

## Inter-Module Communication

### 1. Interface Calls (Synchronous)

**VPS Management → Mailbox Management**
```python
# When deleting a server, remove associated mailboxes
mailbox_interface = MailboxInterface()
mailbox_interface.delete_server_mailboxes(server_id)
```

**Campaign System → Warmup Engine**
```python
# Check if mailbox can send (quota available)
warmup_interface = WarmupInterface()
available = warmup_interface.get_available_quota(mailbox_id, date)
```

**Campaign System → Mailbox Management**
```python
# Get mailbox connection details for sending
mailbox_interface = MailboxInterface()
smtp_config = mailbox_interface.get_smtp_config(mailbox_id)
```

### 2. Event System (Asynchronous)

**Events Flow Chart:**
```
Mailbox Created → Event: 'mailbox.created'
    ├→ Warmup Engine: Initialize warmup stats
    └→ Reporting: Update mailbox count

Campaign Sent → Event: 'campaign.email_sent'
    ├→ Warmup Engine: Reduce available quota
    └→ Reporting: Update send statistics

Server Deleted → Event: 'server.deleted'
    └→ Mailbox Management: Cleanup orphaned mailboxes
```

### 3. Shared Data Access (Through Core)

**All Modules → Core Database Service**
```python
# Never direct SQL, always through Core
from core.database import DatabaseService

class MailboxService:
    def __init__(self):
        self.db = DatabaseService()
    
    def get_mailbox(self, id):
        # Core handles the actual query
        return self.db.get_record('mailboxes', id)
```

## Boundary Enforcement Rules

### Build-Time Checks

1. **Import Validator**
   - Scans all imports in each module
   - Flags any cross-module imports
   - Build fails if violations found

2. **Database Access Audit**
   - Tracks all database queries
   - Ensures modules only access owned tables
   - Logs violations for review

### Runtime Checks

1. **Interface Validation**
   - All interface calls logged
   - Parameter validation enforced
   - Rate limiting applied

2. **Event Bus Security**
   - Events authenticated by source
   - Subscribers verified
   - Malformed events rejected

## Common Scenarios and Solutions

### Scenario 1: Need Mailbox Details in Campaign
**Wrong Way:**
```python
# ❌ Campaign module directly queries mailbox table
mailbox = db.query("SELECT * FROM mailboxes WHERE id = ?", mailbox_id)
```

**Right Way:**
```python
# ✅ Use Mailbox interface
mailbox_interface = MailboxInterface()
mailbox = mailbox_interface.get_mailbox_details(mailbox_id)
```

### Scenario 2: Warmup Needs Server Info
**Wrong Way:**
```python
# ❌ Warmup module imports VPS module
from modules.vps_management.models import Server
server = Server.get(server_id)
```

**Right Way:**
```python
# ✅ Use VPS interface
vps_interface = VPSInterface()
server_info = vps_interface.get_server_info(server_id)
```

### Scenario 3: Report Needs Everything
**Wrong Way:**
```python
# ❌ Reporting directly accesses all tables
campaigns = db.query("SELECT * FROM campaigns")
mailboxes = db.query("SELECT * FROM mailboxes")
```

**Right Way:**
```python
# ✅ Use each module's interface
campaign_stats = CampaignInterface().get_statistics()
mailbox_stats = MailboxInterface().get_statistics()
warmup_stats = WarmupInterface().get_statistics()
```

## Adding New Cross-Module Features

### Process:
1. **Design Phase**
   - Identify all modules involved
   - Design interface methods needed
   - Plan event flows

2. **Review Phase**
   - Architecture review required
   - Document interface changes
   - Update this document

3. **Implementation Phase**
   - Implement interfaces first
   - Add event handlers
   - Test in isolation

4. **Integration Phase**
   - Test module interactions
   - Verify boundaries maintained
   - Update integration tests

## Boundary Violation Consequences

### Immediate Actions:
1. Pull request rejected
2. Build pipeline fails
3. Code review blocked

### Required Fixes:
1. Remove direct dependencies
2. Implement proper interfaces
3. Update tests
4. Document changes

## Testing Boundaries

### Module Isolation Tests
Each module must have tests that run in complete isolation:
```bash
# Run tests for single module only
pytest modules/warmup_engine/tests/ --isolated

# Should work even if other modules deleted
rm -rf modules/campaign_system
pytest modules/warmup_engine/tests/  # Must still pass
```

### Integration Tests
Separate tests verify module interactions:
```bash
# Test interfaces between modules
pytest tests/integration/warmup_campaign_integration.py
```

## Quick Reference

### ✅ ALLOWED:
- Use defined interfaces
- Subscribe to documented events
- Access own database tables via Core
- Emit events for others
- Call Core services

### ❌ FORBIDDEN:
- Import from other modules
- Direct database access
- Read other modules' files
- Bypass interfaces
- Share internal state
- Assume module structure

## Monitoring and Alerts

### Boundary Violations Tracked:
1. Cross-module imports detected
2. Unauthorized database access
3. Interface contract violations
4. Event authentication failures

### Monthly Review:
- Analyze violation patterns
- Update boundaries if needed
- Refactor repeat violations

## Document Updates

This document must be updated when:
1. New modules added
2. Interface changes approved
3. New integration patterns needed
4. Boundaries need adjustment

Update Process:
1. Submit change proposal
2. Architecture review
3. Impact analysis
4. Update with version bump

---

Last Updated: July 2024
Version: 1.0.0
Status: MANDATORY - All code must comply