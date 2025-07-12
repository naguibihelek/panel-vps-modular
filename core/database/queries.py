"""
Core Database Queries

This module provides common database query patterns that can be used
by all modules. These queries enforce best practices and ensure
consistent data access patterns.
"""

from typing import List, Optional, Dict, Any, Type
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from .models import BaseModel


class QueryBuilder:
    """
    A helper class for building complex queries in a consistent way.
    """
    
    def __init__(self, session: Session, model: Type[BaseModel]):
        self.session = session
        self.model = model
        self.query = session.query(model)
    
    def filter_by(self, **kwargs):
        """Add filter conditions"""
        self.query = self.query.filter_by(**kwargs)
        return self
    
    def filter(self, *criteria):
        """Add complex filter conditions"""
        self.query = self.query.filter(*criteria)
        return self
    
    def order_by(self, *columns):
        """Add ordering"""
        self.query = self.query.order_by(*columns)
        return self
    
    def limit(self, limit: int):
        """Limit results"""
        self.query = self.query.limit(limit)
        return self
    
    def offset(self, offset: int):
        """Add offset for pagination"""
        self.query = self.query.offset(offset)
        return self
    
    def count(self) -> int:
        """Get count of results"""
        return self.query.count()
    
    def first(self) -> Optional[BaseModel]:
        """Get first result"""
        return self.query.first()
    
    def all(self) -> List[BaseModel]:
        """Get all results"""
        return self.query.all()
    
    def exists(self) -> bool:
        """Check if any results exist"""
        return self.session.query(self.query.exists()).scalar()


class DatabaseQueries:
    """
    Common database query patterns used across modules.
    """
    
    @staticmethod
    def get_by_id(session: Session, model: Type[BaseModel], id: int) -> Optional[BaseModel]:
        """Get a single record by ID"""
        return session.query(model).filter(model.id == id).first()
    
    @staticmethod
    def get_by_field(session: Session, model: Type[BaseModel], field: str, value: Any) -> Optional[BaseModel]:
        """Get a single record by a specific field value"""
        return session.query(model).filter(getattr(model, field) == value).first()
    
    @staticmethod
    def get_many_by_field(session: Session, model: Type[BaseModel], field: str, value: Any) -> List[BaseModel]:
        """Get multiple records by a specific field value"""
        return session.query(model).filter(getattr(model, field) == value).all()
    
    @staticmethod
    def get_all(session: Session, model: Type[BaseModel], limit: Optional[int] = None) -> List[BaseModel]:
        """Get all records with optional limit"""
        query = session.query(model)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def count(session: Session, model: Type[BaseModel], **filters) -> int:
        """Count records with optional filters"""
        query = session.query(func.count(model.id))
        if filters:
            query = query.filter_by(**filters)
        return query.scalar()
    
    @staticmethod
    def exists(session: Session, model: Type[BaseModel], **filters) -> bool:
        """Check if any records exist with given filters"""
        query = session.query(model).filter_by(**filters)
        return session.query(query.exists()).scalar()
    
    @staticmethod
    def bulk_create(session: Session, model: Type[BaseModel], records: List[Dict[str, Any]]) -> List[BaseModel]:
        """Create multiple records at once"""
        instances = [model(**record) for record in records]
        session.bulk_save_objects(instances, return_defaults=True)
        return instances
    
    @staticmethod
    def bulk_update(session: Session, model: Type[BaseModel], updates: List[Dict[str, Any]]):
        """Update multiple records at once. Each dict must have 'id' field."""
        session.bulk_update_mappings(model, updates)
    
    @staticmethod
    def delete_by_id(session: Session, model: Type[BaseModel], id: int) -> bool:
        """Delete a record by ID"""
        record = session.query(model).filter(model.id == id).first()
        if record:
            session.delete(record)
            return True
        return False
    
    @staticmethod
    def delete_by_field(session: Session, model: Type[BaseModel], field: str, value: Any) -> int:
        """Delete records by field value. Returns count of deleted records."""
        count = session.query(model).filter(getattr(model, field) == value).delete()
        return count
    
    @staticmethod
    def paginate(session: Session, model: Type[BaseModel], page: int = 1, 
                 per_page: int = 20, **filters) -> Dict[str, Any]:
        """
        Paginate query results
        
        Returns:
            Dict with keys: items, total, page, per_page, pages
        """
        query = session.query(model)
        if filters:
            query = query.filter_by(**filters)
        
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def search(session: Session, model: Type[BaseModel], search_fields: List[str], 
               search_term: str) -> List[BaseModel]:
        """
        Search across multiple fields
        
        Args:
            session: Database session
            model: Model class to search
            search_fields: List of field names to search in
            search_term: Term to search for
            
        Returns:
            List of matching records
        """
        conditions = []
        for field in search_fields:
            if hasattr(model, field):
                conditions.append(getattr(model, field).contains(search_term))
        
        if conditions:
            return session.query(model).filter(or_(*conditions)).all()
        return []