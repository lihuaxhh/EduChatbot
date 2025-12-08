# app/crud/chat_session.py

from sqlalchemy.orm import Session
from ..models.chat_sessions import ChatSession
import uuid
from datetime import datetime

def create_chat_session(db: Session, user_id: int) -> str:
    session_id = str(uuid.uuid4())
    new_session = ChatSession(
        session_id=session_id,
        user_id=user_id,
        title="新对话",
        history_json=[],
        is_pinned=False
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return session_id

def get_session_history(db: Session, session_id: str) -> list:
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise ValueError("Session not found")
    return session.history_json or []

def update_session_history(db: Session, session_id: str, new_messages: list):
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise ValueError("Session not found")
    session.history_json = new_messages
    session.updated_at = datetime.utcnow()
    db.commit()

def get_user_sessions(db: Session, user_id: int):
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

def delete_session(db: Session, session_id: str) -> bool:
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if session:
        db.delete(session)
        db.commit()
        return True
    return False