"""
Shared Events Module

This module contains event definitions and utilities for the event-driven
architecture of the system.
"""

from .definitions import (
    SystemEvents,
    AuthEvents,
    VPSEvents,
    MailboxEvents,
    WarmupEvents,
    CampaignEvents,
    ReportingEvents,
    IntegrationEvents,
    EventDefinitions,
    EVENT_SCHEMAS
)

__all__ = [
    'SystemEvents',
    'AuthEvents',
    'VPSEvents',
    'MailboxEvents',
    'WarmupEvents',
    'CampaignEvents',
    'ReportingEvents',
    'IntegrationEvents',
    'EventDefinitions',
    'EVENT_SCHEMAS'
]