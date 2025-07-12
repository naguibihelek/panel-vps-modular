"""
System Event Definitions

This module defines all the events that can be emitted in the system.
Modules should import and use these definitions for consistency.
"""

from enum import Enum
from typing import Dict, Any


class SystemEvents(Enum):
    """Core system events"""
    
    # Startup/Shutdown
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    MODULE_LOADED = "system.module_loaded"
    MODULE_UNLOADED = "system.module_unloaded"
    
    # Health
    HEALTH_CHECK = "system.health_check"
    SERVICE_UNHEALTHY = "system.service_unhealthy"


class AuthEvents(Enum):
    """Authentication related events"""
    
    USER_LOGIN = "auth.user_login"
    USER_LOGOUT = "auth.user_logout"
    USER_LOGIN_FAILED = "auth.login_failed"
    SESSION_EXPIRED = "auth.session_expired"
    PASSWORD_CHANGED = "auth.password_changed"
    API_KEY_CREATED = "auth.api_key_created"
    API_KEY_REVOKED = "auth.api_key_revoked"


class VPSEvents(Enum):
    """VPS Management events"""
    
    SERVER_CREATED = "vps.server_created"
    SERVER_UPDATED = "vps.server_updated"
    SERVER_DELETED = "vps.server_deleted"
    SERVER_STATUS_CHANGED = "vps.server_status_changed"
    DOMAIN_ADDED = "vps.domain_added"
    DOMAIN_REMOVED = "vps.domain_removed"
    DNS_UPDATED = "vps.dns_updated"


class MailboxEvents(Enum):
    """Mailbox Management events"""
    
    MAILBOX_CREATED = "mailbox.created"
    MAILBOX_UPDATED = "mailbox.updated"
    MAILBOX_DELETED = "mailbox.deleted"
    MAILBOX_ENABLED = "mailbox.enabled"
    MAILBOX_DISABLED = "mailbox.disabled"
    PASSWORD_UPDATED = "mailbox.password_updated"
    OAUTH_CONFIGURED = "mailbox.oauth_configured"
    OAUTH_REVOKED = "mailbox.oauth_revoked"
    BULK_IMPORT_STARTED = "mailbox.bulk_import_started"
    BULK_IMPORT_COMPLETED = "mailbox.bulk_import_completed"


class WarmupEvents(Enum):
    """Warmup Engine events"""
    
    WARMUP_ENABLED = "warmup.enabled"
    WARMUP_DISABLED = "warmup.disabled"
    WARMUP_STARTED = "warmup.started"
    WARMUP_COMPLETED = "warmup.completed"
    WARMUP_FAILED = "warmup.failed"
    WARMUP_QUOTA_REACHED = "warmup.quota_reached"
    WARMUP_REPLY_RECEIVED = "warmup.reply_received"
    WARMUP_PLAN_GENERATED = "warmup.plan_generated"
    WARMUP_STATS_UPDATED = "warmup.stats_updated"


class CampaignEvents(Enum):
    """Campaign System events"""
    
    CAMPAIGN_CREATED = "campaign.created"
    CAMPAIGN_UPDATED = "campaign.updated"
    CAMPAIGN_DELETED = "campaign.deleted"
    CAMPAIGN_ACTIVATED = "campaign.activated"
    CAMPAIGN_PAUSED = "campaign.paused"
    CAMPAIGN_RESUMED = "campaign.resumed"
    CAMPAIGN_COMPLETED = "campaign.completed"
    EMAIL_SENT = "campaign.email_sent"
    EMAIL_OPENED = "campaign.email_opened"
    EMAIL_CLICKED = "campaign.email_clicked"
    EMAIL_BOUNCED = "campaign.email_bounced"
    EMAIL_UNSUBSCRIBED = "campaign.email_unsubscribed"
    QUOTA_EXCEEDED = "campaign.quota_exceeded"


class ReportingEvents(Enum):
    """Reporting events"""
    
    REPORT_GENERATED = "reporting.report_generated"
    REPORT_SCHEDULED = "reporting.report_scheduled"
    METRICS_COLLECTED = "reporting.metrics_collected"
    ALERT_TRIGGERED = "reporting.alert_triggered"


class IntegrationEvents(Enum):
    """Integration events"""
    
    WEBHOOK_CONFIGURED = "integration.webhook_configured"
    WEBHOOK_TRIGGERED = "integration.webhook_triggered"
    WEBHOOK_FAILED = "integration.webhook_failed"
    EXTERNAL_SYNC_STARTED = "integration.sync_started"
    EXTERNAL_SYNC_COMPLETED = "integration.sync_completed"
    API_RATE_LIMIT_REACHED = "integration.rate_limit_reached"


class EventDefinitions:
    """
    Central registry of all event definitions.
    """
    
    @staticmethod
    def get_all_events() -> Dict[str, str]:
        """Get all defined events as a dictionary"""
        events = {}
        
        # Collect all events from enum classes
        for enum_class in [
            SystemEvents, AuthEvents, VPSEvents, MailboxEvents,
            WarmupEvents, CampaignEvents, ReportingEvents, IntegrationEvents
        ]:
            for event in enum_class:
                events[event.name] = event.value
        
        return events
    
    @staticmethod
    def is_valid_event(event_name: str) -> bool:
        """Check if an event name is valid"""
        all_events = EventDefinitions.get_all_events()
        return event_name in all_events.values()
    
    @staticmethod
    def get_event_category(event_name: str) -> str:
        """Get the category of an event (e.g., 'auth', 'vps', etc.)"""
        if '.' in event_name:
            return event_name.split('.')[0]
        return 'unknown'


# Event payload schemas (for documentation and validation)
EVENT_SCHEMAS = {
    "auth.user_login": {
        "username": "string",
        "session_id": "string",
        "ip_address": "string (optional)",
        "user_agent": "string (optional)"
    },
    "mailbox.created": {
        "mailbox_id": "integer",
        "email": "string",
        "server_id": "integer",
        "warmup_enabled": "boolean"
    },
    "warmup.completed": {
        "mailbox_id": "integer",
        "emails_sent": "integer",
        "success_rate": "float",
        "date": "string (ISO date)"
    },
    "campaign.email_sent": {
        "campaign_id": "integer",
        "recipient_id": "integer",
        "mailbox_id": "integer",
        "message_id": "string"
    }
    # Add more schemas as needed
}