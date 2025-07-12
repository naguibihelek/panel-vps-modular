"""
Core Database Models

This module contains base model classes and common model functionality
that all modules can inherit from.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
from .connection import Base


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps to models.
    """
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseModel(Base):
    """
    Abstract base model that all other models should inherit from.
    Provides common functionality for all database models.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def update(self, **kwargs):
        """Update model attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_by_id(cls, session, id):
        """Get a record by its ID"""
        return session.query(cls).filter(cls.id == id).first()
    
    @classmethod
    def get_all(cls, session):
        """Get all records"""
        return session.query(cls).all()
    
    @classmethod
    def create(cls, session, **kwargs):
        """Create a new record"""
        instance = cls(**kwargs)
        session.add(instance)
        return instance
    
    def delete(self, session):
        """Delete this record"""
        session.delete(self)
    
    def __repr__(self):
        """Default string representation"""
        return f"<{self.__class__.__name__}(id={self.id})>"