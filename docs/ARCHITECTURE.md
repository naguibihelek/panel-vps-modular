# Email Panel System Architecture

## Document Purpose
This is the MANDATORY architectural blueprint for the Email Panel System. All development MUST comply with this architecture. Violations will result in rejected code and wasted effort.

## System Overview

The Email Panel System is a modular application designed for managing email warmup and campaign operations across multiple mail servers. The architecture enforces strict separation of concerns to prevent feature interference and regression.

### Architectural Principles

1. **Modular Isolation**: Each module operates independently with no direct dependencies on other modules
2. **Interface-Driven Communication**: Modules interact only through defined contracts
3. **Core Stability**: The core foundation layer remains stable and unchangeable
4. **Single Responsibility**: Each module has one clear purpose and scope
5. **Fail-Safe Design**: Module failures cannot cascade to other modules

## System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│                   (Web UI / API Endpoints)                   │
├─────────────────────────────────────────────────────────────┤
│                     MODULE LAYER                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │   VPS    │ │ Mailbox  │ │  Warmup  │ │ Campaign │      │
│  │  Mgmt    │ │   Mgmt   │ │  Engine  │ │  System  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐ ┌──────────┐                                 │
│  │Reporting │ │Integration│                                 │
│  │Analytics │ │    Hub    │                                 │
│  └──────────┘ └──────────┘                                 │
├─────────────────────────────────────────────────────────────┤
│                 INTERFACE LAYER                              │
│              (Module APIs & Contracts)                       │
├─────────────────────────────────────────────────────────────┤
│                CORE FOUNDATION LAYER                         │
│   Database │ Encryption │ Auth │ Config │ Utilities        │
└─────────────────────────────────────────────────────────────┘
```

## Module Communication Patterns

### 1. Direct Interface Calls
Modules expose public interfaces for synchronous operations:
```
WarmupInterface.get_mailbox_quota(mailbox_id) -> int
CampaignInterface.get_active_campaigns() -> List[Campaign]
```

### 2. Event System
Modules emit events for asynchronous notifications:
```
Event: "mailbox.created" -> Warmup Engine subscribes
Event: "campaign.completed" -> Reporting subscribes
```

### 3. Shared Data Access
All database operations go through Core:
```
Module -> Core Database Service -> Database
Never: Module -> Database (FORBIDDEN)
```

## Directory Structure

```
/root/panel-vps-dev/
├── core/                      # Core Foundation Layer
│   ├── __init__.py
│   ├── database/
│   │   ├── connection.py     # Database connections
│   │   ├── models.py         # Base models
│   │   └── queries.py        # Common queries
│   ├── encryption/
│   │   ├── master_key.py     # Key management
│   │   └── crypto.py         # Encrypt/decrypt
│   ├── auth/
│   │   ├── session.py        # Session management
│   │   └── api_keys.py       # API authentication
│   └── utils/
│       ├── logging.py        # System-wide logging
│       └── errors.py         # Error handling
│
├── modules/                   # Service Modules
│   ├── vps_management/
│   │   ├── __init__.py
│   │   ├── interface.py      # Public API
│   │   ├── routes/           # HTTP endpoints
│   │   ├── services/         # Business logic
│   │   ├── models/           # Module-specific models
│   │   └── tests/            # Module tests
│   │
│   ├── mailbox_management/
│   │   └── [same structure]
│   │
│   ├── warmup_engine/
│   │   └── [same structure]
│   │
│   ├── campaign_system/
│   │   └── [same structure]
│   │
│   ├── reporting/
│   │   └── [same structure]
│   │
│   └── integrations/
│       └── [same structure]
│
├── shared/                    # Shared Resources
│   ├── interfaces/           # Interface definitions
│   ├── events/               # Event definitions
│   └── constants/            # System constants
│
└── tests/
    ├── integration/          # Cross-module tests
    └── system/               # Full system tests
```

## Module Interface Standards

Each module MUST provide:

### 1. interface.py
```python
class ModuleInterface:
    """Public API for the module"""
    
    def get_something(self, id: int) -> Optional[Dict]:
        """Read operations"""
        pass
    
    def create_something(self, data: Dict) -> int:
        """Write operations"""
        pass
    
    def emit_event(self, event_name: str, data: Dict):
        """Event emissions"""
        pass
```

### 2. events.py
```python
# Events this module emits
MODULE_EVENTS = {
    'something.created': 'Emitted when something is created',
    'something.updated': 'Emitted when something is updated',
}

# Events this module subscribes to
SUBSCRIPTIONS = [
    'other_module.some_event',
]
```

### 3. models.py
```python
# Module-specific data models
# These do NOT directly map to database tables
# Database access goes through Core
```

## Database Architecture

### Core Tables (Managed by Core)
- servers
- mailboxes  
- warmup_stats_daily
- warmup_targets
- users (authentication)

### Module Tables (Accessed via Core)
- campaigns (Campaign System)
- campaign_recipients (Campaign System)
- oauth_configs (Integrations)
- domains (VPS Management)

### Access Rules
1. Modules NEVER import database models directly
2. All queries go through Core database service
3. Modules request data via Core APIs
4. Core validates all database operations

## Security Architecture

### Encryption
- All passwords encrypted using Core encryption service
- Master key NEVER leaves Core
- Modules receive only decrypted data when authorized

### Authentication
- All requests validated by Core auth service
- Session management handled by Core
- API keys managed centrally

### Audit Trail
- All module operations logged
- Cross-module calls tracked
- Database changes audited

## Development Workflow

### Adding New Features
1. Identify which module owns the feature
2. Update MODULE_CHARTER.md if scope changes
3. Implement within module boundaries
4. Create/update interface if needed
5. Document any new events

### Modifying Existing Features
1. Work only within the owning module
2. Maintain interface compatibility
3. Update tests within module
4. Run integration tests

### Cross-Module Features
1. Design interfaces first
2. Get architecture review
3. Implement in phases
4. Test each integration point

## Forbidden Practices

### NEVER DO THIS:
1. Import from another module directly
2. Access database without Core
3. Share module internals
4. Bypass interfaces
5. Create circular dependencies
6. Store state outside module
7. Hardcode cross-module paths

### ALWAYS DO THIS:
1. Use defined interfaces
2. Emit events for notifications
3. Validate all inputs
4. Handle module failures gracefully
5. Document interface changes
6. Test in isolation

## Migration Strategy

### Current State -> Target Architecture
1. **Phase 1**: Document existing code locations
2. **Phase 2**: Create module structures
3. **Phase 3**: Define all interfaces
4. **Phase 4**: Move code maintaining compatibility
5. **Phase 5**: Remove old structures
6. **Phase 6**: Enforce boundaries

## Compliance Verification

### Automated Checks
- Import validator (no cross-module imports)
- Interface compliance tests
- Event contract validation
- Database access auditing

### Manual Reviews
- Architecture compliance review
- Interface change approval
- Security review for Core changes

## Version Control

### Module Versions
Each module maintains its own version:
- vps_management: 1.0.0
- warmup_engine: 2.1.0
- campaign_system: 1.5.0

### Interface Versions
Interfaces are versioned separately:
- v1: Original interface
- v2: Backward compatible additions
- v3: Breaking changes (requires migration)

## Emergency Procedures

### Module Failure
1. Module isolation prevents cascade
2. Core services remain operational
3. Other modules continue functioning
4. Failed module can be disabled

### Rollback Strategy
1. Each module can be rolled back independently
2. Interface versions allow gradual migration
3. Database changes are reversible

## Enforcement

This architecture is MANDATORY. Violations will result in:
1. Rejected pull requests
2. Failed CI/CD pipelines
3. Code review blocks
4. Required refactoring

## Document Maintenance

This document is the source of truth for system architecture. Changes require:
1. Architecture board review
2. Impact analysis
3. Migration plan
4. Update to all related documents

Last Updated: July 2024
Version: 1.0.0