"""
Core Database Connection Service

This module provides centralized database connection management for the entire system.
All modules MUST use this service for database access. Direct database connections
from modules are FORBIDDEN.
"""

import os
from typing import Generator, Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "panel.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints in SQLite"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DatabaseService:
    """
    Central database service for all database operations.
    This service ensures consistent database access patterns across all modules.
    """
    
    @staticmethod
    @contextmanager
    def get_session() -> Generator[Session, None, None]:
        """
        Get a database session. This should be used as a context manager.
        
        Example:
            with DatabaseService.get_session() as session:
                # perform database operations
                pass
        """
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    @staticmethod
    @contextmanager
    def transaction():
        """
        Create a database transaction context.
        Automatically commits on success, rolls back on exception.
        
        Example:
            with DatabaseService.transaction() as session:
                # perform database operations
                # automatic commit on success
        """
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    def execute_query(query: str, params: Optional[dict] = None):
        """
        Execute a raw SQL query. Use sparingly and only when SQLAlchemy ORM
        cannot handle the query efficiently.
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            
        Returns:
            Query result
        """
        with DatabaseService.transaction() as session:
            result = session.execute(query, params or {})
            return result.fetchall()
    
    @staticmethod
    def get_engine():
        """
        Get the database engine. This should rarely be needed by modules.
        """
        return engine
    
    @staticmethod
    def create_all_tables():
        """
        Create all tables defined in the models. Used for initialization.
        """
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def drop_all_tables():
        """
        Drop all tables. Use with extreme caution!
        """
        Base.metadata.drop_all(bind=engine)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Legacy function for backward compatibility.
    New code should use DatabaseService.get_session()
    """
    with DatabaseService.get_session() as session:
        yield session