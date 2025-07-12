# Branch Structure

This repository follows a simple, clean branching strategy.

## Current Branches

### Production
- `main` - Production-ready code only

### Development
- `develop` - All development work happens here

## Development Workflow

**IMPORTANT**: We do NOT create separate branches for each module. All module development happens directly in the `develop` branch.

### Why?
1. Modules are already separated by directory structure
2. Creating module branches parallel to develop defeats the purpose
3. Simpler workflow with less branch management
4. Changes are incremental and tested continuously

### Process
1. Work directly on `develop` branch
2. Implement modules one at a time
3. Commit frequently with clear messages
4. Test thoroughly before moving to next module
5. When ready for production, merge `develop` → `main`

## Current Status

- ✅ Core Foundation: Complete (in develop)
- 📋 VPS Management: Next (Week 3-4)
- 📋 Other modules: Pending

## Commit Convention

```
feat(module): description     # New features
fix(module): description      # Bug fixes
docs: description            # Documentation
refactor(module): description # Code refactoring
test(module): description    # Tests
```

## Important Notes

- Work directly on `develop` branch
- One module at a time
- Test thoroughly before moving to next module
- Keep commits focused and atomic