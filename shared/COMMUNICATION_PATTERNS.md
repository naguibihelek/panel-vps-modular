# Module Communication Patterns

This document defines the MANDATORY communication patterns that all modules must follow.

## Overview

Modules communicate through three primary mechanisms:
1. **Direct Interface Calls** - Synchronous operations
2. **Event Bus** - Asynchronous notifications
3. **Shared Data Access** - Through Core database service

## 1. Direct Interface Calls

### When to Use
- Synchronous operations that need immediate response
- CRUD operations on module-owned data
- Validation or computation requests

### Pattern
```python
# In your module
from shared.interfaces import get_module_registry

registry = get_module_registry()
mailbox_interface = registry.get_interface("mailbox_management")

# Make interface call
mailbox = mailbox_interface.get_mailbox(mailbox_id)
```

### Rules
- NEVER import from another module directly
- ALWAYS use the registered interface
- Handle ServiceUnavailableError gracefully
- Check module boundaries are not violated

## 2. Event-Based Communication

### When to Use
- Notifications about state changes
- Triggering workflows in other modules
- Broadcasting information to multiple consumers
- Decoupled, asynchronous operations

### Pattern
```python
# Emitting events
from core import get_event_bus
from shared.events import MailboxEvents

event_bus = get_event_bus()
event_bus.emit(
    MailboxEvents.MAILBOX_CREATED.value,
    {"mailbox_id": 123, "email": "user@example.com"},
    source="mailbox_management"
)

# Listening to events
def on_mailbox_created(event):
    mailbox_id = event.data["mailbox_id"]
    # Handle the event

event_bus.on(MailboxEvents.MAILBOX_CREATED.value, on_mailbox_created)
```

### Event Naming Convention
- Format: `module.entity.action`
- Examples:
  - `mailbox.created`
  - `warmup.quota.exceeded`
  - `campaign.email.sent`

### Rules
- Use predefined events from shared.events
- Include all necessary data in event payload
- Don't assume order of event handlers
- Events are fire-and-forget

## 3. Database Access

### When to Use
- Accessing shared data
- Cross-module queries (through views/procedures)
- Transactional operations

### Pattern
```python
# In your module
from shared.interfaces import DatabaseInterface

db = DatabaseInterface()

# Read operation
with db.get_session() as session:
    result = db.get_by_id(MyModel, id)

# Write operation  
with db.transaction() as session:
    instance = MyModel(name="example")
    session.add(instance)
    # Auto-commits on success
```

### Rules
- NEVER access another module's tables directly
- Use Core database service for all operations
- Respect transaction boundaries
- Handle database errors appropriately

## 4. Error Handling

### Pattern
```python
from core.utils import ModuleBoundaryError, ServiceUnavailableError

try:
    # Attempt cross-module operation
    interface = registry.get_interface("other_module")
    result = interface.some_operation()
except ServiceUnavailableError as e:
    # Module not available
    self.logger.error(f"Service unavailable: {e}")
    # Implement fallback
except ModuleBoundaryError as e:
    # Boundary violation
    self.logger.error(f"Boundary violation: {e}")
    # This should not happen in production
except Exception as e:
    # Other errors
    self.error_handler.handle_error(e, {"operation": "cross_module_call"})
```

## 5. Module Lifecycle

### Initialization Order
1. Core Foundation (always first)
2. VPS Management
3. Mailbox Management  
4. Warmup Engine
5. Campaign System
6. Reporting
7. Integrations

### Module States
- `inactive` - Not initialized
- `initialized` - Initialized but not started
- `running` - Active and processing
- `stopping` - Shutdown in progress
- `error` - Failed state

## 6. Best Practices

### DO:
- Use interfaces for synchronous operations
- Use events for notifications
- Validate all inputs from other modules
- Log cross-module communications
- Handle failures gracefully
- Cache frequently accessed data
- Use batch operations when possible

### DON'T:
- Import code from other modules
- Access other modules' database tables
- Assume modules are always available
- Create circular dependencies
- Block on event handlers
- Store large data in events
- Bypass the Core layer

## 7. Performance Considerations

### Interface Calls
- Cache interface references
- Use batch operations
- Implement timeouts
- Consider async alternatives

### Events
- Keep payloads small
- Use event priorities wisely
- Don't rely on event ordering
- Consider event throttling

### Database
- Use connection pooling
- Batch similar operations
- Implement query result caching
- Monitor query performance

## 8. Security

### Authentication
- All cross-module calls should include caller identity
- Use the AuthenticationInterface for verification
- Never pass raw credentials between modules

### Authorization
- Modules should verify permissions for operations
- Use role-based access control
- Log all authorization decisions

### Data Protection
- Encrypt sensitive data using EncryptionInterface
- Never log sensitive information
- Sanitize data before passing between modules

## 9. Testing

### Unit Tests
- Mock module interfaces
- Test error handling
- Verify boundary enforcement

### Integration Tests
- Test actual module interactions
- Verify event flow
- Test failure scenarios

### Example Test
```python
def test_cross_module_communication():
    # Mock the registry
    mock_registry = Mock()
    mock_interface = Mock()
    mock_registry.get_interface.return_value = mock_interface
    
    # Test the communication
    result = my_module.call_other_module()
    
    # Verify
    mock_registry.get_interface.assert_called_with("other_module")
    mock_interface.operation.assert_called_once()
```

## 10. Debugging

### Logging
- Log all cross-module calls at DEBUG level
- Include module names in log entries
- Log event emissions and receptions

### Tracing
- Use correlation IDs for request tracking
- Include timing information
- Track the full call chain

### Monitoring
- Monitor interface call latency
- Track event queue sizes
- Alert on module unavailability

---

Remember: These patterns are MANDATORY. Violations will result in:
- Code review rejection
- System instability  
- Security vulnerabilities
- Maintenance nightmares

Always follow the patterns. When in doubt, ask for clarification.