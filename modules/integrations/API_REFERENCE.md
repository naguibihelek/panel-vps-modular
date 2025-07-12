# Integrations Module - API Reference

## Interface Class: IntegrationsInterface

### Overview
The Integrations Interface provides controlled access to external system connections, webhook management, and API integrations. It handles all communication with third-party services while ensuring security, reliability, and performance.

### Import
```python
from modules.integrations.interface import IntegrationsInterface

# Initialize
integrations_interface = IntegrationsInterface()
```

## Webhook Methods

### register_webhook(config: Dict[str, Any]) -> int
Register a new webhook endpoint for system events.

**Parameters:**
- `config` (Dict): Webhook configuration
  ```python
  {
      'name': 'Slack Campaign Notifications',
      'url': 'https://hooks.slack.com/services/...',
      'events': ['campaign.completed', 'campaign.failed'],
      'auth_type': 'bearer',  # bearer/basic/hmac
      'auth_config': {
          'token': 'xoxb-...'  # or secret for HMAC
      },
      'headers': {
          'X-Custom-Header': 'value'
      },
      'retry_config': {
          'max_attempts': 3,
          'backoff_type': 'exponential',
          'initial_delay': 1000  # milliseconds
      }
  }
  ```

**Returns:**
- Webhook ID (int)

**Exceptions:**
- `InvalidWebhookError`: Invalid configuration
- `WebhookTestFailedError`: Endpoint unreachable

---

### trigger_webhook(event_type: str, data: Dict[str, Any]) -> bool
Manually trigger a webhook for testing or custom events.

**Parameters:**
- `event_type` (str): Event identifier
- `data` (Dict): Event payload

**Returns:**
- `True` if all webhooks triggered successfully
- `False` if any webhook failed (queued for retry)

**Example:**
```python
success = integrations_interface.trigger_webhook(
    'custom.notification',
    {
        'message': 'Manual trigger test',
        'timestamp': '2024-07-11T16:00:00Z'
    }
)
```

---

### get_webhook_health(endpoint_id: int) -> Dict[str, Any]
Get health metrics for a specific webhook endpoint.

**Parameters:**
- `endpoint_id` (int): Webhook endpoint ID

**Returns:**
```python
{
    'endpoint_id': 1,
    'name': 'Slack Notifications',
    'url': 'https://hooks.slack.com/...',
    'status': 'healthy',  # healthy/degraded/failed
    'last_triggered': '2024-07-11T15:45:00Z',
    'last_success': '2024-07-11T15:45:00Z',
    'last_failure': None,
    'metrics': {
        'total_deliveries': 1250,
        'successful_deliveries': 1245,
        'failed_deliveries': 5,
        'average_latency_ms': 250,
        'success_rate': 99.6
    },
    'recent_errors': []
}
```

---

### update_webhook(endpoint_id: int, config: Dict[str, Any]) -> bool
Update webhook configuration.

**Parameters:**
- `endpoint_id` (int): Webhook to update
- `config` (Dict): New configuration (partial updates supported)

**Returns:**
- `True` if updated successfully
- `False` if webhook not found

---

### delete_webhook(endpoint_id: int) -> bool
Remove a webhook endpoint.

**Parameters:**
- `endpoint_id` (int): Webhook to delete

**Returns:**
- `True` if deleted
- `False` if not found

---

### list_webhooks(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]
List all registered webhooks with optional filtering.

**Parameters:**
- `filters` (Dict, optional): Filter criteria
  ```python
  {
      'status': 'active',  # active/paused/failed
      'event_type': 'campaign.*',
      'has_failures': True
  }
  ```

**Returns:**
```python
[
    {
        'endpoint_id': 1,
        'name': 'Slack Notifications',
        'url': 'https://...',
        'events': ['campaign.completed'],
        'status': 'active',
        'health': 'healthy',
        'created_at': '2024-07-01T10:00:00Z'
    }
]
```

---

## Integration Methods

### get_integration_status(integration_name: str) -> Dict[str, Any]
Get current status of an integration.

**Parameters:**
- `integration_name` (str): Integration identifier (e.g., 'salesforce', 'slack')

**Returns:**
```python
{
    'integration_name': 'salesforce',
    'status': 'connected',  # connected/disconnected/error
    'last_sync': '2024-07-11T15:00:00Z',
    'next_sync': '2024-07-11T16:00:00Z',
    'credentials_valid': True,
    'api_quota': {
        'limit': 15000,
        'used': 3500,
        'remaining': 11500,
        'reset_time': '2024-07-12T00:00:00Z'
    },
    'sync_stats': {
        'records_synced_today': 1250,
        'errors_today': 2,
        'average_sync_time': 45.2  # seconds
    }
}
```

---

### sync_data(integration_name: str, data: Dict[str, Any]) -> Dict[str, Any]
Sync data with an external system.

**Parameters:**
- `integration_name` (str): Target integration
- `data` (Dict): Data to sync
  ```python
  {
      'operation': 'upsert',  # create/update/upsert/delete
      'entity': 'contact',
      'records': [
          {
              'email': 'john@example.com',
              'first_name': 'John',
              'last_name': 'Doe',
              'custom_fields': {...}
          }
      ],
      'options': {
          'batch_size': 100,
          'continue_on_error': True
      }
  }
  ```

**Returns:**
```python
{
    'sync_id': 'sync_abc123',
    'status': 'completed',  # completed/partial/failed
    'summary': {
        'total_records': 100,
        'successful': 98,
        'failed': 2,
        'duration_seconds': 12.5
    },
    'errors': [
        {
            'record_index': 45,
            'error': 'Duplicate email address',
            'details': {...}
        }
    ]
}
```

---

### test_integration(integration_name: str) -> Dict[str, Any]
Test integration connectivity and configuration.

**Parameters:**
- `integration_name` (str): Integration to test

**Returns:**
```python
{
    'integration_name': 'salesforce',
    'test_results': {
        'connectivity': {
            'status': 'passed',
            'latency_ms': 150
        },
        'authentication': {
            'status': 'passed',
            'method': 'oauth',
            'token_valid': True
        },
        'permissions': {
            'status': 'passed',
            'read_access': True,
            'write_access': True
        },
        'api_quota': {
            'status': 'passed',
            'quota_available': True
        }
    },
    'overall_status': 'passed',  # passed/warning/failed
    'recommendations': []
}
```

---

### configure_integration(integration_name: str, config: Dict[str, Any]) -> bool
Configure or update an integration.

**Parameters:**
- `integration_name` (str): Integration identifier
- `config` (Dict): Configuration settings
  ```python
  {
      'credentials': {
          'client_id': '...',
          'client_secret': '...',
          'refresh_token': '...'
      },
      'settings': {
          'sync_frequency': '0 */6 * * *',  # Every 6 hours
          'batch_size': 500,
          'field_mapping': {
              'email': 'Email',
              'first_name': 'FirstName'
          }
      },
      'options': {
          'auto_retry': True,
          'notification_email': 'admin@example.com'
      }
  }
  ```

**Returns:**
- `True` if configured successfully
- `False` if configuration invalid

---

## API Management Methods

### get_api_quota(integration_name: str) -> Dict[str, Any]
Get current API quota status for an integration.

**Parameters:**
- `integration_name` (str): Integration identifier

**Returns:**
```python
{
    'integration_name': 'sendgrid',
    'quota_type': 'daily',  # hourly/daily/monthly
    'limit': 100000,
    'used': 45000,
    'remaining': 55000,
    'percentage_used': 45.0,
    'reset_time': '2024-07-12T00:00:00Z',
    'rate_limit': {
        'requests_per_second': 100,
        'burst_limit': 1000
    },
    'warnings': []  # ['Approaching daily limit']
}
```

---

### refresh_credentials(integration_name: str) -> bool
Refresh API credentials (OAuth tokens, etc.).

**Parameters:**
- `integration_name` (str): Integration identifier

**Returns:**
- `True` if refreshed successfully
- `False` if refresh failed

**Note:** Automatic refresh happens before expiry

---

## Event Broadcasting Methods

### broadcast_event(event: Dict[str, Any]) -> Dict[str, Any]
Broadcast an event to all subscribed integrations.

**Parameters:**
- `event` (Dict): Event to broadcast
  ```python
  {
      'event_type': 'campaign.completed',
      'timestamp': '2024-07-11T16:00:00Z',
      'data': {
          'campaign_id': 123,
          'campaign_name': 'Summer Sale',
          'recipients': 50000,
          'sent': 49950,
          'metrics': {...}
      }
  }
  ```

**Returns:**
```python
{
    'broadcast_id': 'bcast_xyz789',
    'webhooks_triggered': 5,
    'integrations_notified': 3,
    'delivery_summary': {
        'immediate_success': 7,
        'queued_for_retry': 1,
        'failed': 0
    }
}
```

---

## Monitoring Methods

### get_integration_logs(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]
Retrieve integration activity logs.

**Parameters:**
- `filters` (Dict, optional): Log filters
  ```python
  {
      'integration_name': 'salesforce',
      'start_time': '2024-07-11T00:00:00Z',
      'end_time': '2024-07-11T23:59:59Z',
      'event_type': 'sync',  # sync/error/webhook/api_call
      'status': 'error'  # success/error/warning
  }
  ```

**Returns:**
```python
[
    {
        'log_id': 'log_123',
        'timestamp': '2024-07-11T15:30:00Z',
        'integration_name': 'salesforce',
        'event_type': 'sync',
        'status': 'success',
        'details': {
            'records_synced': 150,
            'duration_ms': 2500
        }
    }
]
```

---

### get_webhook_deliveries(endpoint_id: int, limit: int = 100) -> List[Dict[str, Any]]
Get recent webhook delivery attempts.

**Parameters:**
- `endpoint_id` (int): Webhook endpoint ID
- `limit` (int): Maximum results (default 100)

**Returns:**
```python
[
    {
        'delivery_id': 'del_456',
        'timestamp': '2024-07-11T15:45:00Z',
        'event_type': 'campaign.completed',
        'status': 'success',
        'attempts': 1,
        'response_code': 200,
        'latency_ms': 245,
        'payload_size': 2048
    }
]
```

---

## Event Subscriptions

### Available Events

The Integrations module emits these events:

```python
from shared.events import subscribe

@subscribe('webhook.failed')
def handle_webhook_failure(event_data):
    endpoint_id = event_data['endpoint_id']
    error = event_data['error']
    # Handle failure
```

**Events:**
- `webhook.registered` - New webhook created
- `webhook.triggered` - Webhook fired
- `webhook.delivered` - Successful delivery
- `webhook.failed` - Delivery failed
- `integration.connected` - Integration active
- `integration.disconnected` - Integration down
- `integration.sync_complete` - Sync finished
- `api.quota_warning` - Low quota alert

---

## Error Handling

### Exception Hierarchy
```
IntegrationsError (base)
├── WebhookError
│   ├── InvalidWebhookError
│   ├── WebhookDeliveryError
│   └── WebhookTestFailedError
├── IntegrationError
│   ├── IntegrationNotFoundError
│   ├── AuthenticationError
│   └── SyncError
├── APIError
│   ├── QuotaExceededError
│   ├── RateLimitError
│   └── APITimeoutError
└── ConfigurationError
```

---

## Rate Limits

To ensure system stability:

- `register_webhook`: Max 100 webhooks total
- `trigger_webhook`: Max 1000 calls/minute
- `sync_data`: Based on integration limits
- `get_integration_logs`: Max 100 calls/minute

---

## Best Practices

1. **Handle webhook failures gracefully**
   ```python
   @subscribe('webhook.failed')
   def handle_failure(data):
       if data['consecutive_failures'] > 5:
           # Disable webhook temporarily
           integrations_interface.update_webhook(
               data['endpoint_id'],
               {'status': 'paused'}
           )
   ```

2. **Monitor API quotas**
   ```python
   quota = integrations_interface.get_api_quota('salesforce')
   if quota['percentage_used'] > 80:
       # Reduce sync frequency or batch size
       pass
   ```

3. **Test integrations regularly**
   ```python
   # Schedule daily integration tests
   for integration in ['salesforce', 'slack', 'hubspot']:
       result = integrations_interface.test_integration(integration)
       if result['overall_status'] != 'passed':
           alert_admin(integration, result)
   ```

4. **Use appropriate sync strategies**
   ```python
   # Batch large datasets
   sync_result = integrations_interface.sync_data(
       'salesforce',
       {
           'operation': 'upsert',
           'entity': 'contact',
           'records': large_dataset,
           'options': {
               'batch_size': 500,
               'continue_on_error': True
           }
       }
   )
   ```

---

**Version**: 1.0.0  
**Interface Stability**: Stable  
**Last Updated**: July 2024