"""
Database Interface

This interface defines how modules interact with the Core database service.
All modules MUST use this interface for database operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type, Generator
from contextlib import contextmanager


class IDatabaseInterface(ABC):
    """
    Database interface that all modules must use for data access.
    This ensures consistent database access patterns and prevents
    direct database connections from modules.
    """
    
    @abstractmethod
    def get_session(self) -> Generator:
        """Get a database session"""
        pass
    
    @abstractmethod
    @contextmanager
    def transaction(self):
        """Create a transactional context"""
        pass
    
    @abstractmethod
    def get_by_id(self, model: Type, id: int) -> Optional[Any]:
        """Get a record by ID"""
        pass
    
    @abstractmethod
    def get_by_field(self, model: Type, field: str, value: Any) -> Optional[Any]:
        """Get a record by field value"""
        pass
    
    @abstractmethod
    def get_all(self, model: Type, limit: Optional[int] = None) -> List[Any]:
        """Get all records"""
        pass
    
    @abstractmethod
    def create(self, model: Type, **data) -> Any:
        """Create a new record"""
        pass
    
    @abstractmethod
    def update(self, model: Type, id: int, **data) -> Optional[Any]:
        """Update a record"""
        pass
    
    @abstractmethod
    def delete(self, model: Type, id: int) -> bool:
        """Delete a record"""
        pass
    
    @abstractmethod
    def count(self, model: Type, **filters) -> int:
        """Count records"""
        pass
    
    @abstractmethod
    def exists(self, model: Type, **filters) -> bool:
        """Check if records exist"""
        pass
    
    @abstractmethod
    def paginate(self, model: Type, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """Paginate results"""
        pass
    
    @abstractmethod
    def search(self, model: Type, search_fields: List[str], search_term: str) -> List[Any]:
        """Search across fields"""
        pass


class DatabaseInterface(IDatabaseInterface):
    """
    Concrete implementation of the database interface.
    This is what modules will actually use.
    """
    
    def __init__(self):
        # Import here to avoid circular imports
        from core.database import DatabaseService, DatabaseQueries
        self.service = DatabaseService
        self.queries = DatabaseQueries
    
    def get_session(self):
        """Get a database session"""
        return self.service.get_session()
    
    @contextmanager
    def transaction(self):
        """Create a transactional context"""
        with self.service.transaction() as session:
            yield session
    
    def get_by_id(self, model: Type, id: int) -> Optional[Any]:
        """Get a record by ID"""
        with self.get_session() as session:
            return self.queries.get_by_id(session, model, id)
    
    def get_by_field(self, model: Type, field: str, value: Any) -> Optional[Any]:
        """Get a record by field value"""
        with self.get_session() as session:
            return self.queries.get_by_field(session, model, field, value)
    
    def get_all(self, model: Type, limit: Optional[int] = None) -> List[Any]:
        """Get all records"""
        with self.get_session() as session:
            return self.queries.get_all(session, model, limit)
    
    def create(self, model: Type, **data) -> Any:
        """Create a new record"""
        with self.transaction() as session:
            instance = model(**data)
            session.add(instance)
            session.flush()
            return instance
    
    def update(self, model: Type, id: int, **data) -> Optional[Any]:
        """Update a record"""
        with self.transaction() as session:
            instance = self.queries.get_by_id(session, model, id)
            if instance:
                for key, value in data.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                session.flush()
            return instance
    
    def delete(self, model: Type, id: int) -> bool:
        """Delete a record"""
        with self.transaction() as session:
            return self.queries.delete_by_id(session, model, id)
    
    def count(self, model: Type, **filters) -> int:
        """Count records"""
        with self.get_session() as session:
            return self.queries.count(session, model, **filters)
    
    def exists(self, model: Type, **filters) -> bool:
        """Check if records exist"""
        with self.get_session() as session:
            return self.queries.exists(session, model, **filters)
    
    def paginate(self, model: Type, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """Paginate results"""
        with self.get_session() as session:
            return self.queries.paginate(session, model, page, per_page, **filters)
    
    def search(self, model: Type, search_fields: List[str], search_term: str) -> List[Any]:
        """Search across fields"""
        with self.get_session() as session:
            return self.queries.search(session, model, search_fields, search_term)