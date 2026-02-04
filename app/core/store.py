from typing import Dict
from app.core.types import SessionId, LivenessChallenge
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class LivenessSession:
    session_id: SessionId
    challenge: LivenessChallenge
    created_at: datetime
    is_verified: bool = False

class SessionStore:
    def __init__(self):
        self._sessions: Dict[str, LivenessSession] = {}

    def create_session(self, session_id: SessionId, challenge: LivenessChallenge):
        self._sessions[session_id] = LivenessSession(
            session_id=session_id,
            challenge=challenge,
            created_at=datetime.utcnow()
        )

    def get_session(self, session_id: str) -> LivenessSession | None:
        return self._sessions.get(session_id)

    def mark_verified(self, session_id: str):
        if session_id in self._sessions:
            self._sessions[session_id].is_verified = True

    def cleanup(self, ttl_seconds: int = 300):
        now = datetime.utcnow()
        expired = [
            sid for sid, sess in self._sessions.items() 
            if (now - sess.created_at).total_seconds() > ttl_seconds
        ]
        for sid in expired:
            del self._sessions[sid]

# Singleton
session_store = SessionStore()
