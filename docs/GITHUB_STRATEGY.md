# GitHub Repository Strategy

## Overview
This document defines the GitHub workflow, branching strategy, and compliance rules for the Email Enhancement Project. All contributors must follow these guidelines to maintain code quality and system stability.

## Repository Structure

```
email-panel-enhancement/
├── .github/
│   ├── workflows/
│   │   ├── test.yml          # Automated testing
│   │   └── lint.yml          # Code quality checks
│   └── pull_request_template.md
├── src/                      # Source code
│   ├── models/              # Database models
│   ├── utils/               # Utility functions
│   ├── api/                 # API endpoints
│   └── templates/           # UI templates
├── migrations/              # Database migrations
│   ├── phase1/
│   ├── phase2/
│   └── ...
├── tests/                   # Test suite
│   ├── unit/
│   └── integration/
├── scripts/                 # Deployment & utility scripts
├── docs/                    # Documentation
│   └── phases/             # Implementation phases
├── config/                  # Configuration templates
├── .gitignore
├── README.md
├── CONTRIBUTING.md
└── requirements.txt
```

## Branching Strategy

### Branch Types

1. **main** - Production-ready code only
   - Protected branch - no direct pushes
   - Only receives merges from develop after thorough testing
   - All tests must pass

2. **develop** - Primary development branch
   - ALL development work happens here
   - This is where you work day-to-day
   - Must be stable and tested
   - Merges to main when ready for production

### PROJECT BRANCHES UNDER DEVELOP
**IMPORTANT**: All project work happens in branches under the `develop/` namespace. This maintains modularity and allows separate management of each project phase.

#### Branch Structure:
```
develop/phase1-database
develop/phase2-passwords
develop/phase3-gmail
develop/phase4-campaigns
develop/modular-architecture
develop/[project-name]
```

#### Rules:
- NO branches parallel to develop (e.g., `feature/something` at the same level as develop)
- ALL project branches MUST be under `develop/` namespace
- Each project phase gets its own branch for modular management
- Merge project branches → develop → main when complete and tested

### When to Merge develop → main
- After thorough testing on develop
- When a set of features is complete and stable
- Before major deployments
- Typically weekly or bi-weekly, depending on activity

### Branch Flow Diagram

```
main (production)
  ↑
  │ (merge when stable & tested)
  │
develop (integration branch)
  ↑
  ├── develop/phase1-database
  ├── develop/phase2-passwords
  ├── develop/phase3-gmail
  ├── develop/modular-architecture
  └── develop/[other-projects]
```

### Simple Workflow
1. **Create/checkout project branch**: `git checkout -b develop/project-name` or `git checkout develop/project-name`
2. **Pull latest**: `git pull origin develop/project-name`
3. **Work on project branch**: Make changes, test, commit
4. **Push to project branch**: `git push origin develop/project-name`
5. **When project phase complete**: Create PR to merge project branch → develop
6. **When ready for production**: Merge develop → main

## Commit Message Convention

All commits must follow this format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples:
```bash
feat(phase1): add campaign tables to database schema

- Added campaigns, campaign_recipients, campaign_responses tables
- Created indexes for performance
- Included rollback script

Implements: Phase 1 requirements
```

```bash
fix(passwords): correct encryption key path for Gmail accounts

- Fixed hardcoded path to use config variable
- Added path validation

Fixes: #23
```

## Pull Request Process

### PR Requirements:

1. **Title Format**: `[Phase X] Brief description`
   - Example: `[Phase 1] Database schema migration`

2. **Description Template**:
   ```markdown
   ## Summary
   Brief description of changes

   ## Phase
   Phase 1: Database Schema

   ## Changes
   - [ ] List specific changes
   - [ ] Include file modifications

   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed

   ## Rollback Plan
   Describe how to revert these changes if needed

   ## Checklist
   - [ ] Code follows project style
   - [ ] Documentation updated
   - [ ] No sensitive data exposed
   - [ ] Database backup created (if applicable)
   ```

3. **Review Requirements**:
   - Self-review first
   - At least one approval required
   - All CI checks must pass
   - No merge conflicts

## Testing Requirements

### Before Creating PR:

1. **Local Testing**:
   ```bash
   # Run all tests
   python -m pytest tests/

   # Run specific phase tests
   python -m pytest tests/phase1/

   # Check code style
   ruff check src/
   ```

2. **Database Testing**:
   - Test migrations on copy of production data
   - Verify rollback procedures
   - Check data integrity

3. **Integration Testing**:
   - Test with subset of real mailboxes
   - Verify warmup system still functions
   - Check API endpoints

## Release Process

### Version Tagging:
```bash
# Phase completion tags
git tag -a phase1-complete -m "Phase 1: Database schema complete"

# Release versions
git tag -a v1.0.0 -m "Initial release with Phases 1-3"
```

### Release Checklist:
1. [ ] All phase tests pass
2. [ ] Documentation updated
3. [ ] CHANGELOG.md updated
4. [ ] Database migrations tested
5. [ ] Rollback plan documented
6. [ ] Tag created
7. [ ] Production backup completed

## Security Guidelines

### Never Commit:
- Passwords or API keys
- Gmail app passwords
- Master encryption key
- Production database files
- Email addresses (use examples)

### Use Instead:
- Environment variables
- Config templates with `.example` suffix
- Encrypted credential storage

## Compliance Rules

### Every Session Must:

1. **Start with**:
   ```bash
   # For new project
   git checkout develop
   git pull origin develop
   git checkout -b develop/project-name
   
   # For existing project
   git checkout develop/project-name
   git pull origin develop/project-name
   ```

2. **During work**:
   - Work on your project branch under develop/
   - Commit frequently with clear messages
   - Push to remote regularly
   - Run tests before committing

3. **End with**:
   ```bash
   git push origin develop/project-name
   ```

### Phase Completion Criteria:

1. All planned features implemented
2. Tests written and passing
3. Documentation updated
4. PR approved and merged
5. Phase tag created
6. Production deployment successful

## Quick Reference Commands

```bash
# Start new project branch
git checkout develop
git pull origin develop
git checkout -b develop/modular-architecture

# Continue existing project
git checkout develop/modular-architecture
git pull origin develop/modular-architecture

# Make changes and commit
git add -A
git commit -m "feat(core): implement database service layer"

# Push to project branch
git push origin develop/modular-architecture

# When project phase complete (create PR)
# PR: develop/modular-architecture → develop

# When ready to deploy to production
git checkout main
git pull origin main
git merge develop
git push origin main

# Tag a release (optional)
git tag -a v1.0.0-modular -m "Modular architecture core foundation"
git push origin v1.0.0-modular
```

## GitHub Actions (CI/CD)

### Automated Checks:
1. Python linting (ruff)
2. Unit test execution
3. Migration script validation
4. Security scan for credentials

### Required Status Checks:
- All tests must pass
- No linting errors
- No security violations

## Emergency Procedures

### Hotfix Process:
```bash
# Create from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# Fix and test
# ...

# Merge to main and develop
git checkout main
git merge hotfix/critical-bug
git checkout develop
git merge hotfix/critical-bug
```

### Rollback Process:
1. Identify last working tag
2. Create hotfix from that tag
3. Revert problematic commits
4. Deploy hotfix immediately

## Questions or Exceptions

If you need to deviate from these guidelines:
1. Document the reason
2. Get approval before proceeding
3. Update this document if it's a permanent change

---

**Remember**: The warmup system is production-critical. Always prioritize stability over speed.