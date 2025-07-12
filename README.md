# Email Panel System - Modular Architecture

This is the modular architecture implementation of the Email Panel System, a complete rewrite focused on maintainability, scalability, and clear separation of concerns.

## Overview

The system manages email warmup operations and marketing campaigns across multiple mail servers using a strict modular architecture with well-defined boundaries.

## Architecture

### Core Foundation
- **Database Service**: Centralized data access
- **Encryption Service**: Password and data encryption
- **Authentication Service**: User auth and sessions
- **Event Bus**: Inter-module communication
- **Utilities**: Logging, error handling

### Modules
1. **VPS Management**: Server and domain management
2. **Mailbox Management**: Email account operations
3. **Warmup Engine**: Automated email warmup
4. **Campaign System**: Marketing campaign execution
5. **Reporting**: Analytics and statistics
6. **Integrations**: External system connections

## Project Structure

```
panel-vps-modular/
├── core/                  # Core Foundation services
│   ├── auth/             # Authentication & sessions
│   ├── database/         # Database access layer
│   ├── encryption/       # Encryption services
│   └── utils/            # Common utilities
├── shared/               # Shared resources
│   ├── interfaces/       # Module interfaces
│   ├── events/          # Event definitions
│   └── constants/       # System constants
├── modules/              # Feature modules
│   ├── vps_management/
│   ├── mailbox_management/
│   ├── warmup_engine/
│   ├── campaign_system/
│   ├── reporting/
│   └── integrations/
├── migrations/           # Database migrations
├── tests/               # Test suites
├── scripts/             # Deployment scripts
└── docs/                # Documentation
```

## Development Guidelines

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `develop/core-foundation` - Core implementation
- `develop/module-*` - Module implementations

### Module Rules
1. No direct imports between modules
2. Communication via interfaces and events only
3. Each module has its own database tables
4. Modules must be independently testable

### Commit Convention
```
type(scope): description

Types: feat, fix, docs, refactor, test, chore
Scope: core, module name, or component
```

## Getting Started

1. Clone the repository
2. Set up virtual environment
3. Install dependencies
4. Configure environment
5. Run tests

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Module Definitions](docs/MODULE_DEFINITIONS.md)
- [Communication Patterns](docs/COMMUNICATION_PATTERNS.md)
- [Migration Plan](docs/MIGRATION_PLAN.md)

## Status

This is a complete rewrite of the email panel system, replacing the previous monolithic architecture with a clean, modular design.

## License

Proprietary - All rights reserved