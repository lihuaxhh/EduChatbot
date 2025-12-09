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
    row = db.query(ChatSession.history_json).filter(ChatSession.session_id == session_id).first()
    if not row:
        raise ValueError("Session not found")
    return (row[0] or [])

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

    # 仅更新需要的列，避免选择整行触发不存在列的错误
    from sqlalchemy import text
    now = datetime.utcnow()
    db.execute(
        text(
            """
            UPDATE chat_sessions
            SET 
                history_json = :history,
                title = CASE WHEN title IS NULL OR title = '新对话' THEN COALESCE(:title, title) ELSE title END,
                updated_at = :updated
            WHERE session_id = :sid
            """
        ),
        {
            "history": new_messages,
            "title": name,
            "updated": now,
            "sid": session_id,
        },
    )
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
        .all()
    )

def delete_session(db: Session, session_id: str) -> bool:
    # 直接执行删除避免选择整行
    deleted = db.query(ChatSession).filter(ChatSession.session_id == session_id).delete()
    db.commit()
    return bool(deleted)
