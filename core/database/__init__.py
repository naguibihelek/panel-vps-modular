"""
Core Database Module

This module provides centralized database access for all system modules.
All database operations MUST go through this module.
"""

from .connection import (
    DatabaseService,
    get_db,
    Base,
    engine,
    SessionLocal
)
from .models import (
    BaseModel,
    TimestampMixin
)
from .queries import (
    DatabaseQueries,
    QueryBuilder
)

__all__ = [
    # Connection
    'DatabaseService',
    'get_db',
    'Base',
    'engine',
    'SessionLocal',
    
    # Models
    'BaseModel',
    'TimestampMixin',
    
    # Queries
    'DatabaseQueries',
    'QueryBuilder'
]