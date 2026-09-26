import time
import uuid
import threading
from typing import Dict, List, Optional, Any
from ..schemas.assistant import PropertySlots
from ..core.config import settings

class AssistantSession:
    """
    Encapsulates bounded conversation state and accumulated property slots for a single user session.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id: str = session_id or str(uuid.uuid4())
        self.messages: List[Dict[str, str]] = []
        self.accumulated_slots: PropertySlots = PropertySlots()
        self.created_at: float = time.time()
        self.last_accessed: float = time.time()

    def is_expired(self, ttl_minutes: int = 30) -> bool:
        """Returns True if session has been inactive longer than ttl_minutes."""
        return (time.time() - self.last_accessed) > (ttl_minutes * 60)

    def touch(self) -> None:
        """Updates last_accessed timestamp."""
        self.last_accessed = time.time()

    def add_message(self, role: str, content: str) -> None:
        """Appends a message and enforces the bounded max_messages constraint."""
        self.touch()
        self.messages.append({"role": role, "content": content})
        # Keep bounded history
        if len(self.messages) > settings.SESSION_MAX_MESSAGES:
            self.messages = self.messages[-settings.SESSION_MAX_MESSAGES:]

    def merge_slots(self, new_slots: PropertySlots) -> None:
        """
        Merges newly extracted slots into the accumulated slot state.
        Preserves existing non-null attributes unless explicitly overwritten.
        """
        self.touch()
        for field in PropertySlots.model_fields.keys():
            val = getattr(new_slots, field, None)
            if val is not None:
                setattr(self.accumulated_slots, field, val)

    def reset_slots(self) -> None:
        """Clears accumulated slots while keeping session ID."""
        self.touch()
        self.accumulated_slots = PropertySlots()

    def reset(self) -> None:
        """Completely resets messages and slots."""
        self.touch()
        self.messages.clear()
        self.accumulated_slots = PropertySlots()


class SessionManager:
    """
    Thread-safe in-memory session manager with automatic TTL eviction.
    """

    def __init__(self, ttl_minutes: int = 30):
        self.ttl_minutes = ttl_minutes
        self._sessions: Dict[str, AssistantSession] = {}
        self._lock = threading.Lock()

    def get_or_create_session(self, session_id: Optional[str] = None) -> AssistantSession:
        """
        Retrieves an active session or creates a new one if not found or expired.
        """
        with self._lock:
            self._cleanup_expired()

            if session_id and session_id in self._sessions:
                session = self._sessions[session_id]
                if not session.is_expired(self.ttl_minutes):
                    session.touch()
                    return session

            # Create new session
            new_id = session_id if (session_id and len(session_id) > 8) else str(uuid.uuid4())
            new_session = AssistantSession(session_id=new_id)
            self._sessions[new_id] = new_session
            return new_session

    def reset_session(self, session_id: str) -> bool:
        """Resets the specified session if present."""
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].reset()
                return True
            return False

    def delete_session(self, session_id: str) -> bool:
        """Deletes session from memory."""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def get_active_sessions_count(self) -> int:
        """Returns the number of currently active non-expired sessions."""
        with self._lock:
            self._cleanup_expired()
            return len(self._sessions)

    def _cleanup_expired(self) -> None:
        """Removes sessions that have exceeded the TTL."""
        now = time.time()
        expired_ids = [
            sid for sid, s in self._sessions.items()
            if (now - s.last_accessed) > (self.ttl_minutes * 60)
        ]
        for sid in expired_ids:
            del self._sessions[sid]

session_manager = SessionManager(ttl_minutes=settings.SESSION_TTL_MINUTES)
