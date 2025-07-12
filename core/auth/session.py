"""
Session Management

This module handles user sessions and authentication state.
"""

import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class UserSession:
    """Represents an authenticated user session"""
    session_id: str
    username: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if the session has expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_inactive(self, timeout_minutes: int = 30) -> bool:
        """Check if the session has been inactive too long"""
        inactive_time = datetime.utcnow() - self.last_activity
        return inactive_time > timedelta(minutes=timeout_minutes)
    
    def update_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = datetime.utcnow()


class SessionManager:
    """
    Manages user sessions for the authentication system.
    
    This is an in-memory session store. In production, this should
    be replaced with Redis or database-backed sessions.
    """
    
    def __init__(self, session_timeout_hours: int = 24, 
                 inactivity_timeout_minutes: int = 30):
        """
        Initialize the session manager.
        
        Args:
            session_timeout_hours: Total session lifetime in hours
            inactivity_timeout_minutes: Inactivity timeout in minutes
        """
        self._sessions: Dict[str, UserSession] = {}
        self.session_timeout_hours = session_timeout_hours
        self.inactivity_timeout_minutes = inactivity_timeout_minutes
    
    def create_session(self, username: str, session_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session for a user.
        
        Args:
            username: Username for the session
            session_data: Optional additional session data
            
        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)
        now = datetime.utcnow()
        
        session = UserSession(
            session_id=session_id,
            username=username,
            created_at=now,
            last_activity=now,
            expires_at=now + timedelta(hours=self.session_timeout_hours),
            data=session_data or {}
        )
        
        self._sessions[session_id] = session
        self._cleanup_expired_sessions()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            UserSession if valid and active, None otherwise
        """
        session = self._sessions.get(session_id)
        
        if session is None:
            return None
        
        # Check if expired or inactive
        if session.is_expired() or session.is_inactive(self.inactivity_timeout_minutes):
            self.destroy_session(session_id)
            return None
        
        # Update activity timestamp
        session.update_activity()
        return session
    
    def update_session_data(self, session_id: str, data: Dict[str, Any]):
        """
        Update session data.
        
        Args:
            session_id: Session ID to update
            data: Data to merge into session
        """
        session = self.get_session(session_id)
        if session:
            session.data.update(data)
    
    def destroy_session(self, session_id: str):
        """
        Destroy a session.
        
        Args:
            session_id: Session ID to destroy
        """
        self._sessions.pop(session_id, None)
    
    def destroy_user_sessions(self, username: str):
        """
        Destroy all sessions for a specific user.
        
        Args:
            username: Username whose sessions to destroy
        """
        sessions_to_remove = [
            sid for sid, session in self._sessions.items()
            if session.username == username
        ]
        
        for sid in sessions_to_remove:
            self.destroy_session(sid)
    
    def get_active_sessions(self) -> Dict[str, UserSession]:
        """
        Get all active sessions.
        
        Returns:
            Dictionary of active sessions
        """
        self._cleanup_expired_sessions()
        return self._sessions.copy()
    
    def get_user_sessions(self, username: str) -> list[UserSession]:
        """
        Get all sessions for a specific user.
        
        Args:
            username: Username to get sessions for
            
        Returns:
            List of active sessions for the user
        """
        return [
            session for session in self._sessions.values()
            if session.username == username and not session.is_expired()
        ]
    
    def _cleanup_expired_sessions(self):
        """Remove expired and inactive sessions"""
        expired_sessions = [
            sid for sid, session in self._sessions.items()
            if session.is_expired() or session.is_inactive(self.inactivity_timeout_minutes)
        ]
        
        for sid in expired_sessions:
            self._sessions.pop(sid, None)
    
    def session_count(self) -> int:
        """Get the number of active sessions"""
        self._cleanup_expired_sessions()
        return len(self._sessions)
    
    def clear_all_sessions(self):
        """Clear all sessions (use with caution!)"""
        self._sessions.clear()


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """
    Get the global session manager instance.
    
    Returns:
        SessionManager instance
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager