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

def normalize_markdown_latex(text: str) -> str:
    try:
        import re
        s = text or ""
        # 将 $$ 换行块转为 \[ ... \]（避免 markdown 段落拆分影响）
        s = re.sub(r"(^|\r?\n)\s*\$\$\s*(?:\r?\n)([\s\S]*?)(?:\r?\n)\s*\$\$(?=\r?\n|$)", r"\1\\[\2\\]", s)
        # 将 [ ... ] 中的对齐/分段环境转换为 \[ ... \]
        s = re.sub(
            r"\[\s*([\s\S]*?\\begin\{(?:aligned|cases)\}[\s\S]*?\\end\{(?:aligned|cases)\}[\s\S]*?)\s*\]",
            r"\\[\1\\]", s)
        # 行尾单反斜杠换行修正为 \\（避免对代码块的影响，仅限普通文本）
        s = re.sub(r"(?<!\\)\\\s*$", r"\\\\", s, flags=re.MULTILINE)
        # 函数名与变量连写：\sin alpha -> \sin\alpha、\cos x -> \cos x（保留合法写法）
        s = re.sub(r"\\(sin|cos|tan|cot|sec|csc)\s+([a-zA-Z])", r"\\\1\\\2", s)
        # 向量参数补齐：\vec a -> \vec{a}
        s = re.sub(r"\\vec\s+([a-zA-Z])", r"\\vec{\1}", s)
        # log 下标空格：\log _a -> \log_a
        s = re.sub(r"\\log\s+_([a-zA-Z])", r"\\log_\1", s)
        # 常见误写控制序列：\x、\y 等移除反斜杠
        s = re.sub(r"\\([xy])\b", r"\1", s)
        return s
    except Exception:
        return text

async def stream_chat(messages: list):
    """流式调用 DashScope qwen3-max"""
    api_key = get_api_key()

    try:
        guard = {
            "role": "system",
            "content": (
                "你是“学习助手”。只处理学习相关问题（学科知识、题目解析、解题思路、学习方法、考试策略、作业辅导、知识图谱解释等）。"
                "当收到与学习无关的话题时，礼貌拒绝并回复："
                "“我主要负责解答学习相关的问题，请不要和我聊学习无关的话题哦。”"
                "\n输出规范：使用中文与 Markdown；数学公式用 LaTeX。"
                "\n分隔：行内用$...$或\\(...\\)，块级优先用\\[...\\]；如使用$$请写在同一段内（$$ ... $$），禁止将$$单独占行。"
                "\n排版：多行公式使用\\begin{aligned} ... \\end{aligned}，每行以\\\\换行，并使用&对齐。"
                "\n函数与符号：写作\\sin\\alpha、\\cos\\beta、\\tan\\theta、\\ln x、\\log_a M、\\frac{a}{b}。"
                "\n向量：写作\\vec{v}，模长写作|\\vec{v}|。"
                "\n不要输出单个反斜杠续行，不要把函数名与变量分开（如“\\sin alpha”）。"
                "\n回答需结构化，步骤清晰，给出关键公式与结论。"
            )
        }
        final_messages = [guard] + messages
        responses = Generation.call(
            api_key=api_key,
            model="qwen3-max",
            messages=final_messages,
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
        {"role": "assistant", "content": normalize_markdown_latex(ai_reply)}
    ])
    update_session_history(db, session_id, history)
