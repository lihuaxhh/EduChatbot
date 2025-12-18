# app/api/chat.py

from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..services.chat import stream_chat, save_message_to_history, normalize_markdown_latex
from ..crud.chat_session import create_chat_session, get_user_sessions, delete_session, get_session_history
from ..db.session import get_db
from ..core.config import settings
from ..models.user import User
from .deps import get_current_user
import json

router = APIRouter()


@router.post("/chat")
async def chat(
        request: Request,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    data = await request.json()
    message = data.get("message")
    session_id = data.get("session_id")
    user_id = current_user.id

    print("DATABASE_URL:", settings.database_url)
    print("user_id:", user_id, "session_id:", session_id)

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    if not session_id:
        session_id = create_chat_session(db, user_id)
        print("created session_id:", session_id)

    try:
        history = get_session_history(db, session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = history + [{"role": "user", "content": message}]

    full_ai_response = ""  # 用于收集完整回复

    async def generate():
        nonlocal full_ai_response
        async for chunk in stream_chat(messages):
            full_ai_response += chunk
            # 维持真正的流式输出：逐块写回前端
            yield chunk

    # 定义后台保存函数
    def save_history_task():
        try:
            # 注意：这里需要重新获取 db session（不能复用 FastAPI 的依赖）
            from ..db.session import SessionLocal
            db_local = SessionLocal()
            try:
                save_message_to_history(db_local, session_id, message, full_ai_response)
            finally:
                db_local.close()
        except Exception as e:
            print(f"⚠️ Failed to save chat history: {e}")

    # 添加后台任务
    background_tasks.add_task(save_history_task)

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8", headers={"X-Session-Id": session_id})


@router.post("/chat/save")
async def save_chat_history(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = await request.json()
    session_id = data.get("session_id")
    user_msg = data.get("user_message")
    ai_reply = data.get("ai_reply")

    if not all([session_id, user_msg, ai_reply]):
        raise HTTPException(status_code=400, detail="Missing fields")

    save_message_to_history(db, session_id, user_msg, ai_reply)
    return {"status": "saved"}


@router.get("/sessions")
async def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = get_user_sessions(db, current_user.id)
    return [
        {
            "session_id": s.session_id,
            "title": s.title,
            "is_pinned": s.is_pinned,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat()
        }
        for s in sessions
    ]


@router.delete("/sessions/{session_id}")
async def remove_session(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # TODO: Check if session belongs to user
    success = delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted"}

@router.post("/sessions")
async def create_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sid = create_chat_session(db, current_user.id)
    return {"session_id": sid}

@router.get("/sessions/{session_id}/history")
async def session_history(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        history = get_session_history(db, session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")
    return history
