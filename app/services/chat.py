# app/services/chat.py

import os
from fastapi import HTTPException
from dashscope import Generation
from ..crud.chat_session import get_session_history, update_session_history
from sqlalchemy.orm import Session


def get_api_key():
    key = os.getenv("DASHSCOPE_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="DASHSCOPE_API_KEY not set in .env")
    return key


async def stream_chat(messages: list):
    """流式调用 DashScope qwen3-max"""
    api_key = get_api_key()

    try:
        responses = Generation.call(
            api_key=api_key,
            model="qwen3-max",
            messages=messages,
            stream=True,
            incremental_output=True,
            result_format="message"
        )

        for response in responses:
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"DashScope error: {response.code} - {response.message}"
                )

            choices = response.output.get("choices", [])
            if choices and "message" in choices[0]:
                content = choices[0]["message"].get("content", "")
                if content:
                    yield content
            elif "text" in response.output:
                text = response.output.get("text", "")
                if text:
                    yield text

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stream failed: {str(e)}")


def save_message_to_history(db: Session, session_id: str, user_msg: str, ai_reply: str):
    history = get_session_history(db, session_id)
    history.extend([
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": ai_reply}
    ])
    update_session_history(db, session_id, history)