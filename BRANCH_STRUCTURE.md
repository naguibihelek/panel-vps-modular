# Branch Structure

This repository follows a modular branching strategy that mirrors the code architecture.

## Current Branches

### Production
- `main` - Production-ready code only

### Integration
- `develop` - Integration branch where all modules merge

### Module Development Branches
- `develop-core-foundation` - Core Foundation implementation ✓ COMPLETE
- `develop-vps-management` - VPS Management module (Week 3-4)
- `develop-mailbox-management` - Mailbox Management module (Week 5-6)
- `develop-warmup-engine` - Warmup Engine module (Week 7-8)
- `develop-campaign-system` - Campaign System module (Week 9-10)
- `develop-reporting` - Reporting module (Week 11-12)
- `develop-integrations` - Integrations module (Week 13-14)

## Branch Naming Convention

Due to Git limitations, we use `develop-module-name` instead of `develop/module-name`.

## Workflow

1. Create module branch from develop: `git checkout -b develop-module-name`
2. Implement module following architecture guidelines
3. Test thoroughly
4. Create PR to merge into develop
5. After all modules tested together, merge develop → main

## Status

- Core Foundation: Complete and ready for integration
- Other modules: Pending implementation

## Important Notes

- Each module branch should only contain changes for that specific module
- Follow module boundaries strictly
- Test modules in isolation before integration
- Maintain backward compatibility during migration