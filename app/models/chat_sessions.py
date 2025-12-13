# app/models/chat_sessions.py

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base
from datetime import datetime

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID 格式
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), default="新对话", nullable=False)
    session_name = Column(String(100), nullable=True)
    history_json = Column(JSON, nullable=False, default=list)  # [{"role": "user", "content": "..."}]
    is_pinned = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)
