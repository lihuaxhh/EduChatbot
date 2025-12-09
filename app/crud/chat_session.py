# app/crud/chat_session.py

from sqlalchemy.orm import Session
from ..models.chat_sessions import ChatSession
import uuid
import json
from datetime import datetime
from sqlalchemy import text

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
    # Use scalar query for better performance if just fetching one column
    # Also handle the case where history_json might be returned as string by some drivers
    row = db.query(ChatSession.history_json).filter(ChatSession.session_id == session_id).first()
    if not row:
        raise ValueError("Session not found")
    
    history = row[0]
    if isinstance(history, str):
        try:
            return json.loads(history)
        except:
            return []
    return (history or [])

def update_session_history(db: Session, session_id: str, new_messages: list):
    # 生成标题（仅首次或占位标题时）
    name = None
    for m in new_messages:
        if isinstance(m, dict) and m.get("role") == "user":
            t = (m.get("content") or "").strip().replace("\n", " ")
            if len(t) > 20:
                t = t[:20] + "..."
            name = t or "新对话"
            break

    # Use ORM update which handles JSON serialization automatically
    # This is safer than raw SQL for JSON fields
    update_data = {
        "history_json": new_messages,
        "updated_at": datetime.now()
    }
    
    # Check if we should update title
    # Logic: Update title if it's currently "新对话" or None
    current_title = db.query(ChatSession.title).filter(ChatSession.session_id == session_id).scalar()
    if (not current_title or current_title == "新对话") and name:
        update_data["title"] = name

    db.query(ChatSession).filter(ChatSession.session_id == session_id).update(update_data)
    db.commit()

def get_user_sessions(db: Session, user_id: int):
    return (
        db.query(
            ChatSession.session_id,
            ChatSession.title,
            ChatSession.is_pinned,
            ChatSession.created_at,
            ChatSession.updated_at,
        )
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )

def delete_session(db: Session, session_id: str) -> bool:
    # 直接执行删除避免选择整行
    deleted = db.query(ChatSession).filter(ChatSession.session_id == session_id).delete()
    db.commit()
    return bool(deleted)
