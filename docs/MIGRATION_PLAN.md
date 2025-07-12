# Migration Plan: Current State to Modular Architecture

## Overview
This document outlines the step-by-step process to migrate from the current mixed codebase to the clean modular architecture. This migration MUST be followed in order to prevent breaking production systems.

## Current State Analysis

### Existing Structure (Mixed/Tangled)
```
app/
├── routes/           # All routes mixed together
│   ├── servers.py    # VPS management
│   ├── mailboxes.py  # Multiple concerns
│   ├── warmup_*.py   # Warmup features
│   ├── outreach*.py  # Campaign features
│   └── ...
├── utils/            # Mixed utilities
│   ├── warmup_planner.py
│   ├── email_sender.py
│   └── ...
├── models.py         # All models together
└── database.py       # Shared database access
```

### Problems with Current State:
1. **No Clear Boundaries** - Features intertwined
2. **Direct Database Access** - Any file can query any table
3. **Circular Dependencies** - Routes import utils import routes
4. **Missing Features** - 404 errors on previously working routes
5. **Regression Risk** - Changes break unrelated features

## Target State (Modular)

### Clean Module Structure:
```
core/                 # Stable foundation
modules/
├── vps_management/   # Isolated VPS features
├── mailbox_mgmt/     # Isolated mailbox features
├── warmup_engine/    # Isolated warmup features
├── campaign_system/  # Isolated campaign features
├── reporting/        # Isolated reporting
└── integrations/     # Isolated integrations
```

## Migration Phases

### Phase 0: Preparation (Week 1)
**Goal**: Set up infrastructure without breaking anything

1. **Create Module Directories**
   ```bash
   mkdir -p modules/{vps_management,mailbox_management,warmup_engine}
   mkdir -p modules/{campaign_system,reporting,integrations}
   mkdir -p core/{database,encryption,auth,utils}
   mkdir -p shared/{interfaces,events,constants}
   ```

2. **Create Placeholder Files**
   - Add `__init__.py` to all directories
   - Create empty `interface.py` in each module
   - Create `MODULE_CHARTER.md` in each module

3. **Set Up Core Services**
   ```
   core/database/service.py     # Database abstraction
   core/encryption/service.py   # Encryption service
   core/auth/service.py         # Auth service
   ```

4. **No Code Movement Yet** - Just structure

---

### Phase 1: Core Foundation (Week 2)
**Goal**: Establish core services that modules will depend on

1. **Database Service**
   - Move database connection logic to `core/database/`
   - Create abstraction layer for queries
   - Add logging for all database access

2. **Encryption Service**
   - Move master key handling to `core/encryption/`
   - Create encrypt/decrypt interface
   - Secure credential management

3. **Authentication Service**
   - Move session management to `core/auth/`
   - Centralize login/logout logic
   - API key management

4. **Testing**
   - Core services must work independently
   - All existing features still use old code

---

### Phase 2: First Module - Reporting (Week 3)
**Goal**: Migrate the least dependent module first

1. **Why Reporting First?**
   - Read-only module (lowest risk)
   - No dependencies on other modules
   - Good test case for process

2. **Migration Steps**
   ```
   a. Copy reporting routes to modules/reporting/routes/
   b. Create ReportingInterface with read methods
   c. Update routes to use Core database service
   d. Test in isolation
   e. Update main.py to use new routes
   f. Remove old routes
   ```

3. **Validation**
   - All reporting pages load
   - Stats display correctly
   - No write operations

---

### Phase 3: VPS Management Module (Week 4)
**Goal**: Migrate server management features

1. **Identify Components**
   - Routes: servers.py, domains.py
   - Models: Server, Domain
   - Features: CRUD operations

2. **Migration Steps**
   ```
   a. Create VPSInterface
   b. Move routes maintaining URLs
   c. Implement proper domain ownership
   d. Add event emissions
   e. Test server operations
   ```

3. **Handle Dependencies**
   - When deleting server, emit event
   - Mailbox module will subscribe later

---

### Phase 4: Mailbox Management Module (Week 5)
**Goal**: Migrate mailbox features with OAuth support

1. **Complex Migration**
   - Multiple files involved
   - OAuth configurations
   - Bulk operations

2. **Migration Steps**
   ```
   a. Create MailboxInterface
   b. Move individual mailbox routes
   c. Move bulk operations
   d. Move OAuth handling
   e. Subscribe to server.deleted event
   ```

3. **Critical Testing**
   - Mailbox creation/deletion
   - Password management
   - OAuth flow
   - Bulk imports

---

### Phase 5: Warmup Engine Module (Week 6-7)
**Goal**: Migrate the most critical system

1. **High Risk Migration**
   - Production critical
   - Complex scheduling logic
   - Must not interrupt daily warmups

2. **Parallel Operation Strategy**
   ```
   a. Copy warmup code to module
   b. Create WarmupInterface
   c. Run NEW code in test mode
   d. Compare outputs with OLD code
   e. Switch over when verified
   f. Remove old code
   ```

3. **Rollback Plan**
   - Keep old code for 1 week
   - Switch back if issues
   - Monitor closely

---

### Phase 6: Campaign System Module (Week 8)
**Goal**: Migrate campaign features

1. **Migration Complexity**
   - Depends on Mailbox module
   - Depends on Warmup module
   - Must maintain quotas

2. **Migration Steps**
   ```
   a. Create CampaignInterface
   b. Move campaign routes
   c. Implement quota checking via WarmupInterface
   d. Use MailboxInterface for sending
   e. Test campaign operations
   ```

---

### Phase 7: Integrations Module (Week 9)
**Goal**: Migrate external integrations

1. **Components**
   - BCC processing
   - Webhook handling
   - OAuth flows
   - Response forwarding

2. **Migration Steps**
   ```
   a. Create IntegrationInterface
   b. Move webhook routes
   c. Move response processing
   d. Test external connections
   ```

---

### Phase 8: Cleanup and Enforcement (Week 10)
**Goal**: Remove old code and enforce boundaries

1. **Remove Old Structure**
   ```bash
   # After verification
   rm -rf app/routes/warmup_*.py
   rm -rf app/routes/outreach*.py
   # etc.
   ```

2. **Enable Enforcement**
   - Activate import validator
   - Enable boundary checks
   - Update CI/CD pipeline

3. **Documentation**
   - Update all paths in docs
   - Create migration guide
   - Archive old structure

## Migration Rules

### During EVERY Phase:

1. **Maintain Backwards Compatibility**
   - Old URLs must work
   - Database schema unchanged
   - API contracts maintained

2. **Test Continuously**
   ```bash
   # Before each commit
   python test_pre_commit.py
   
   # After each phase
   ./run_all_tests.sh admin password
   ```

3. **Parallel Operation**
   - New code alongside old
   - Switch over when verified
   - Remove old only when stable

4. **Rollback Ready**
   - Tag before each phase
   - Document rollback steps
   - Test rollback procedure

## Risk Mitigation

### High Risk Areas:
1. **Warmup Engine** - Production critical
2. **Database Access** - Data integrity
3. **Authentication** - Security critical

### Mitigation Strategies:
1. **Feature Flags**
   ```python
   if settings.USE_NEW_WARMUP_MODULE:
       from modules.warmup_engine import WarmupInterface
   else:
       from app.utils import old_warmup
   ```

2. **Gradual Rollout**
   - Test with single mailbox
   - Expand to 10%
   - Full rollout when stable

3. **Monitoring**
   - Track module performance
   - Compare old vs new
   - Alert on anomalies

## Success Criteria

### Each Phase Complete When:
1. ✅ All tests pass
2. ✅ No 404 errors
3. ✅ Features work identically
4. ✅ Performance maintained
5. ✅ No boundary violations
6. ✅ Documentation updated

### Migration Complete When:
1. ✅ All modules migrated
2. ✅ Old code removed
3. ✅ Boundaries enforced
4. ✅ Team trained
5. ✅ Documentation complete

## Rollback Procedures

### Phase Rollback:
```bash
# Tag before migration
git tag pre-phase-X

# If issues, rollback
git checkout pre-phase-X
systemctl restart panel-api
```

### Module Rollback:
```python
# In settings
ENABLED_MODULES = {
    'reporting': True,
    'vps_management': True,
    'warmup_engine': False,  # Rollback this module
}
```

## Timeline Summary

| Week | Phase | Module | Risk Level |
|------|-------|---------|-----------|
| 1 | Phase 0 | Setup | Low |
| 2 | Phase 1 | Core | Medium |
| 3 | Phase 2 | Reporting | Low |
| 4 | Phase 3 | VPS Mgmt | Medium |
| 5 | Phase 4 | Mailbox | Medium |
| 6-7 | Phase 5 | Warmup | HIGH |
| 8 | Phase 6 | Campaign | Medium |
| 9 | Phase 7 | Integrations | Low |
| 10 | Phase 8 | Cleanup | Low |

## Post-Migration

### New Development Process:
1. Identify module for feature
2. Work within module only
3. Use interfaces for integration
4. Test in isolation
5. Document changes

### Maintenance:
1. Monthly architecture review
2. Boundary violation report
3. Performance monitoring
4. Update documentation

---

**IMPORTANT**: This migration cannot be rushed. Each phase must be completed and verified before proceeding. The warmup system is production-critical and must not be disrupted.

Last Updated: July 2024
Version: 1.0.0