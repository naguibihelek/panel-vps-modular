# Reporting Module

## Quick Overview

The Reporting module provides comprehensive analytics and insights across all system operations. It aggregates data from every module to deliver real-time dashboards, scheduled reports, and actionable intelligence while maintaining strict read-only access to source data.

## Key Responsibilities
- 📊 Real-time dashboards for all modules
- 📈 Scheduled and on-demand reports
- 🔍 Data aggregation and analytics
- 📉 Trend analysis and predictions
- 🎯 Performance metrics and KPIs
- 🚨 Anomaly detection and alerting

## Module Status
- **Version**: 1.0.0
- **Stability**: Stable
- **Dependencies**: Core Foundation, All Other Modules (read-only)
- **Required By**: None (end-point module)

## Quick Start

### For Module Users (Other Modules)
```python
from modules.reporting.interface import ReportingInterface

reporting = ReportingInterface()

# Get system health
health = reporting.get_system_health_score()
print(f"System Health: {health['overall_score']}/100")

# Get metrics
volume = reporting.get_metric_history('email_volume', days=7)

# Generate report
report = reporting.generate_report(report_id=1)
```

### For Report Users

1. **View Dashboards**: `/reports/dashboards`
2. **Generate Reports**: `/reports/generate`
3. **Schedule Reports**: `/reports/schedule`
4. **View Analytics**: `/reports/analytics`

## Documentation

- 📋 [Module Scope](MODULE_SCOPE.md) - Detailed boundaries and responsibilities
- 🔧 [Features](FEATURES.md) - Complete feature list
- 📚 [API Reference](API_REFERENCE.md) - Interface documentation

## Database Tables

This module owns:
- `report_definitions` - Report configurations
- `report_schedules` - Recurring report schedules
- `report_history` - Generated report archive
- `dashboard_configs` - Dashboard layouts
- `metric_snapshots` - Historical metric data
- `report_cache` - Performance optimization

## Available Dashboards

### System Dashboards
- **Executive**: High-level overview
- **Operations**: Detailed operations metrics
- **Financial**: Cost and ROI analysis

### Module Dashboards
- **Warmup**: Progress and health tracking
- **Campaigns**: Performance analytics
- **Mailboxes**: Utilization and status
- **Servers**: Infrastructure monitoring

## Standard Reports

### Daily Reports
1. **Operations Summary** - 24-hour snapshot
2. **Error Report** - Issues and resolutions
3. **Warmup Progress** - Daily advancement

### Weekly Reports
1. **Performance Analysis** - Trends and insights
2. **Campaign Summary** - Results and ROI
3. **System Health** - Infrastructure status

### Monthly Reports
1. **Executive Summary** - Strategic overview
2. **Financial Analysis** - Cost breakdown
3. **Growth Metrics** - Expansion tracking

## Key Metrics Tracked

### Volume Metrics
- Total emails sent
- Emails by module
- Peak send rates
- Queue depths

### Performance Metrics
- Delivery rates
- Open/click rates
- Bounce rates
- Response times

### Health Metrics
- System uptime
- Error rates
- Resource usage
- Module health scores

## Common Operations

### View Real-time Dashboard
```python
dashboard = reporting.get_dashboard_data('executive')
for widget in dashboard['widgets']:
    print(f"{widget['title']}: {widget['value']}")
```

### Generate Custom Report
```python
report = reporting.generate_report(
    report_id=4,  # Campaign Performance
    parameters={
        'start_date': '2024-07-01',
        'end_date': '2024-07-31',
        'campaign_ids': [1, 2, 3]
    }
)
print(f"Report URL: {report['download_url']}")
```

### Track Metric Trends
```python
# Get email volume for last 30 days
history = reporting.get_metric_history('email_volume', days=30)
for point in history:
    print(f"{point['timestamp']}: {point['value']}")
```

## Events

### Emitted Events
- `report.generated`
- `report.scheduled`
- `report.failed`
- `dashboard.updated`
- `metric.anomaly`

### Subscribed Events
The Reporting module subscribes to ALL events from other modules to maintain comprehensive analytics.

## Data Retention

### Retention Policies
- **Raw Data**: 90 days
- **Aggregated Data**: 2 years
- **Reports**: 7 years
- **Snapshots**: 1 year

### Archival Process
- Automatic compression after 30 days
- Monthly archival to cold storage
- On-demand restoration available

## Performance Considerations

- Dashboards use caching (30s-5m)
- Reports generated asynchronously
- Read replicas for data access
- Query optimization for large datasets

## Troubleshooting

### Dashboard Not Loading
1. Check cache status
2. Verify data sources
3. Review error logs
4. Check permissions

### Report Generation Fails
1. Validate parameters
2. Check data availability
3. Review timeout settings
4. Check disk space

### Metrics Missing
1. Verify event flow
2. Check aggregation jobs
3. Review retention policy
4. Validate calculations

## Best Practices

1. **Use Appropriate Time Ranges**
   - Don't request years of minute-level data
   - Use aggregated data for long ranges

2. **Schedule Heavy Reports Off-Peak**
   - Large reports at 2-4 AM
   - Stagger multiple schedules

3. **Cache Dashboard Data**
   - Respect refresh intervals
   - Don't poll unnecessarily

4. **Monitor Report Sizes**
   - Set reasonable limits
   - Use filters effectively

## Support

- 📝 Log Location: `/var/log/reporting/`
- 🐛 Report Issues: Create ticket with module tag
- 📧 Module Owner: Analytics Team

---

For development and contribution guidelines, see the main [ARCHITECTURE.md](/root/ARCHITECTURE.md) document.