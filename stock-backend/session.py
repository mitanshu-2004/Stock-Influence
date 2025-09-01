from datetime import datetime, timedelta
from typing import Dict, Any
from config import  SESSION_TIMEOUT_HOURS

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, session_id: str, data: Dict[str, Any]):
        self.sessions[session_id] = {
            **data,
            "created_at": datetime.now(),
            "last_accessed": datetime.now()
        }

    def get_session(self, session_id: str) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if session:
            session["last_accessed"] = datetime.now()
        return session

    def update_session(self, session_id: str, new_data: Dict[str, Any]):
        session = self.get_session(session_id)
        if session:
            session.update(new_data)

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def cleanup_sessions(self):
        now = datetime.now()
        expired = [
            sid for sid, s in self.sessions.items()
            if now - s["last_accessed"] > timedelta(hours=SESSION_TIMEOUT_HOURS)
        ]
        for sid in expired:
            self.delete_session(sid)