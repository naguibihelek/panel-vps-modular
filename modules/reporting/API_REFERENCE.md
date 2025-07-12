# Reporting Module - API Reference

## Interface Class: ReportingInterface

### Overview
The Reporting Interface provides read-only access to system analytics, metrics, and report generation. It aggregates data from all modules to provide comprehensive insights while maintaining strict read-only access to source data.

### Import
```python
from modules.reporting.interface import ReportingInterface

# Initialize
reporting_interface = ReportingInterface()
```

## Dashboard Methods

### get_dashboard_data(dashboard_id: str) -> Dict[str, Any]
Retrieve real-time dashboard data with all widgets.

**Parameters:**
- `dashboard_id` (str): Dashboard identifier (e.g., 'executive', 'operations', 'warmup')

**Returns:**
```python
{
    'dashboard_id': 'executive',
    'name': 'Executive Dashboard',
    'last_updated': '2024-07-11T15:30:00Z',
    'widgets': [
        {
            'widget_id': 'total_emails_sent',
            'type': 'metric',
            'title': 'Emails Sent Today',
            'value': 125000,
            'change': '+12.5%',
            'trend': 'up',
            'sparkline': [110000, 115000, 120000, 125000]
        },
        {
            'widget_id': 'system_health',
            'type': 'gauge',
            'title': 'System Health',
            'value': 98,
            'max': 100,
            'status': 'healthy',
            'thresholds': {'danger': 60, 'warning': 80}
        },
        {
            'widget_id': 'active_campaigns',
            'type': 'list',
            'title': 'Active Campaigns',
            'items': [
                {'name': 'Summer Sale', 'progress': 75, 'eta': '2h'},
                {'name': 'Newsletter', 'progress': 45, 'eta': '4h'}
            ]
        }
    ],
    'refresh_interval': 30
}
```

**Available Dashboards:**
- `executive` - High-level overview
- `operations` - Detailed operations
- `warmup` - Warmup analytics
- `campaigns` - Campaign performance
- `mailboxes` - Mailbox management

---

### create_custom_dashboard(config: Dict[str, Any]) -> str
Create a new custom dashboard configuration.

**Parameters:**
- `config` (Dict): Dashboard configuration
  ```python
  {
      'name': 'My Custom Dashboard',
      'layout': 'grid',  # grid/list/custom
      'widgets': [
          {
              'type': 'metric',
              'metric': 'daily_email_volume',
              'position': {'x': 0, 'y': 0, 'w': 2, 'h': 1}
          }
      ],
      'refresh_interval': 60,
      'is_public': False
  }
  ```

**Returns:**
- Dashboard ID (string)

---

## Report Generation Methods

### generate_report(report_id: int, parameters: Dict = None) -> Dict[str, Any]
Generate a report on-demand with optional parameters.

**Parameters:**
- `report_id` (int): Report definition ID
- `parameters` (Dict, optional): Report parameters

**Parameter Examples:**
```python
# Date range
parameters = {
    'start_date': '2024-07-01',
    'end_date': '2024-07-31'
}

# Campaign specific
parameters = {
    'campaign_id': 123,
    'include_recipients': True
}

# Filter options
parameters = {
    'servers': [1, 2, 3],
    'status': 'active',
    'min_engagement': 20
}
```

**Returns:**
```python
{
    'report_id': 1,
    'name': 'Monthly Campaign Performance',
    'generated_at': '2024-07-11T15:45:00Z',
    'parameters': {...},
    'format': 'pdf',
    'status': 'completed',
    'download_url': '/reports/download/abc123',
    'expires_at': '2024-07-18T15:45:00Z',
    'summary': {
        'total_campaigns': 25,
        'total_sent': 1250000,
        'avg_open_rate': 24.5,
        'avg_click_rate': 3.2
    }
}
```

**Standard Report IDs:**
- `1` - Daily Operations Report
- `2` - Weekly Performance Report
- `3` - Monthly Executive Summary
- `4` - Campaign Performance Report
- `5` - Warmup Progress Report
- `6` - System Health Report

---

### schedule_report(report_id: int, schedule: Dict[str, Any]) -> int
Schedule recurring report generation.

**Parameters:**
- `report_id` (int): Report to schedule
- `schedule` (Dict): Schedule configuration

**Schedule Format:**
```python
{
    'frequency': 'daily',  # daily/weekly/monthly/custom
    'time': '09:00',  # HH:MM in UTC
    'timezone': 'America/New_York',
    'day_of_week': 1,  # For weekly (1=Monday)
    'day_of_month': 1,  # For monthly
    'cron': '0 9 * * 1',  # For custom
    'recipients': ['admin@example.com'],
    'format': 'pdf',  # pdf/excel/csv
    'parameters': {
        'include_charts': True
    }
}
```

**Returns:**
- Schedule ID (int)

---

## Metric Methods

### get_metric_history(metric: str, days: int = 7, dimensions: Dict = None) -> List[Dict[str, Any]]
Retrieve historical values for a specific metric.

**Parameters:**
- `metric` (str): Metric identifier
- `days` (int): Number of days of history (max 90)
- `dimensions` (Dict, optional): Filter dimensions

**Available Metrics:**
- `email_volume` - Total emails sent
- `open_rate` - Average open rate
- `click_rate` - Average click rate
- `bounce_rate` - Average bounce rate
- `warmup_progress` - Warmup completion
- `system_uptime` - System availability
- `error_rate` - System error rate
- `queue_depth` - Email queue size

**Returns:**
```python
[
    {
        'timestamp': '2024-07-11T00:00:00Z',
        'value': 125000,
        'dimensions': {
            'module': 'campaign',
            'server_id': 1
        }
    },
    # ... more data points
]
```

---

### get_system_health_score() -> Dict[str, Any]
Calculate current system health score with component breakdown.

**Parameters:** None

**Returns:**
```python
{
    'overall_score': 95,
    'status': 'healthy',  # healthy/warning/critical
    'components': {
        'servers': {
            'score': 100,
            'status': 'healthy',
            'details': 'All servers operational'
        },
        'warmup': {
            'score': 92,
            'status': 'healthy',
            'details': '92% of warmups on track'
        },
        'campaigns': {
            'score': 88,
            'status': 'warning',
            'details': 'High bounce rate detected'
        },
        'database': {
            'score': 98,
            'status': 'healthy',
            'details': 'Low query latency'
        }
    },
    'recommendations': [
        'Investigate campaign bounce rates',
        'Consider adding more servers'
    ],
    'last_updated': '2024-07-11T15:50:00Z'
}
```

---

### get_module_statistics(module: str) -> Dict[str, Any]
Get comprehensive statistics for a specific module.

**Parameters:**
- `module` (str): Module name ('warmup', 'campaign', 'mailbox', 'vps')

**Returns:**
```python
# Example for warmup module
{
    'module': 'warmup',
    'statistics': {
        'active_warmups': 150,
        'total_sent_today': 35000,
        'average_progress': 65.5,
        'success_rate': 98.2,
        'completed_this_week': 12,
        'failing_warmups': 3
    },
    'trends': {
        'volume_7d': [30000, 31000, 32000, 33000, 34000, 34500, 35000],
        'success_rate_7d': [97.5, 97.8, 98.0, 98.1, 98.2, 98.2, 98.2]
    },
    'top_issues': [
        {'mailbox_id': 45, 'issue': 'Low success rate', 'severity': 'warning'}
    ]
}
```

---

## Analytics Methods

### get_engagement_analytics(campaign_id: int = None, days: int = 30) -> Dict[str, Any]
Analyze email engagement patterns.

**Parameters:**
- `campaign_id` (int, optional): Specific campaign or all
- `days` (int): Analysis period

**Returns:**
```python
{
    'period': '30 days',
    'engagement_funnel': {
        'sent': 1000000,
        'delivered': 980000,
        'opened': 245000,
        'clicked': 32000,
        'converted': 2500
    },
    'by_hour': {
        '09': {'opens': 15.2, 'clicks': 2.1},
        '10': {'opens': 18.5, 'clicks': 2.8},
        # ... 24 hours
    },
    'by_day': {
        'monday': {'opens': 22.5, 'clicks': 3.1},
        'tuesday': {'opens': 24.1, 'clicks': 3.3},
        # ... 7 days
    },
    'device_breakdown': {
        'desktop': 45.5,
        'mobile': 48.2,
        'tablet': 6.3
    },
    'client_breakdown': {
        'gmail': 35.2,
        'outlook': 28.5,
        'apple_mail': 15.3,
        'other': 21.0
    }
}
```

---

### get_latest_snapshot(metric_type: str) -> Dict[str, Any]
Get the most recent snapshot for a metric type.

**Parameters:**
- `metric_type` (str): Type of metric snapshot

**Returns:**
```python
{
    'metric_type': 'system_overview',
    'snapshot_time': '2024-07-11T15:00:00Z',
    'data': {
        'total_mailboxes': 500,
        'active_campaigns': 5,
        'emails_queued': 25000,
        'warmup_active': 150,
        'system_load': 0.65
    }
}
```

---

## Export Methods

### export_data(export_config: Dict[str, Any]) -> Dict[str, Any]
Export data for external analysis.

**Parameters:**
```python
export_config = {
    'type': 'metrics',  # metrics/events/raw
    'metrics': ['email_volume', 'open_rate'],
    'start_date': '2024-07-01',
    'end_date': '2024-07-31',
    'format': 'csv',  # csv/json/excel
    'grouping': 'daily'  # hourly/daily/weekly
}
```

**Returns:**
```python
{
    'export_id': 'exp_123456',
    'status': 'processing',  # processing/completed/failed
    'download_url': None,  # Set when completed
    'expires_at': '2024-07-18T15:00:00Z',
    'size_bytes': 0  # Set when completed
}
```

---

## Event Subscriptions

### Available Events

The Reporting module emits these events:

```python
from shared.events import subscribe

@subscribe('report.generated')
def handle_report_ready(event_data):
    report_id = event_data['report_id']
    download_url = event_data['download_url']
    # Send notification or process
```

**Events:**
- `report.generated` - Report ready
- `report.scheduled` - Schedule created
- `report.failed` - Generation failed
- `dashboard.updated` - Dashboard refreshed
- `metric.anomaly` - Anomaly detected
- `snapshot.captured` - Snapshot taken

---

## Error Handling

### Exception Hierarchy
```
ReportingError (base)
├── ReportNotFoundError
├── DashboardNotFoundError
├── MetricNotFoundError
├── InvalidParametersError
├── DataAccessError
├── GenerationTimeoutError
└── ExportError
```

---

## Rate Limits

To ensure performance:

- `get_dashboard_data`: Max 100 calls/minute
- `generate_report`: Max 10 concurrent
- `get_metric_history`: Max 1000 calls/minute
- `export_data`: Max 5 concurrent

---

## Best Practices

1. **Cache dashboard data**
   ```python
   # Use provided refresh intervals
   dashboard = reporting_interface.get_dashboard_data('executive')
   cache_duration = dashboard['refresh_interval']
   ```

2. **Use appropriate time ranges**
   ```python
   # Don't request excessive history
   history = reporting_interface.get_metric_history('email_volume', days=30)
   ```

3. **Schedule heavy reports**
   ```python
   # Generate large reports during off-peak
   schedule = {
       'frequency': 'daily',
       'time': '02:00'  # 2 AM UTC
   }
   ```

4. **Handle report generation async**
   ```python
   # Don't block on report generation
   result = reporting_interface.generate_report(1)
   if result['status'] == 'processing':
       # Check back later or wait for event
       pass
   ```

---

**Version**: 1.0.0  
**Interface Stability**: Stable  
**Last Updated**: July 2024