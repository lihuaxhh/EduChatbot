from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import base64
import os

def image_to_data_url(image_path: str) -> str:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    mime = "image/jpeg" if image_path.lower().endswith(".jpg") else "image/png"
    return f"data:{mime};base64,{b64}"

def _get_llm():
    key = os.getenv("DASHSCOPE_API_KEY")
    base = os.getenv("DASHSCOPE_BASE_URL")
    if not key or not base:
        raise RuntimeError("DASHSCOPE env missing")
    return ChatOpenAI(
        model="qwen3-vl-plus",
        api_key=key,
        base_url=base,
        temperature=0.0,
        max_tokens=2048
    )

def extract_answer_from_image(image_path: str) -> str:
    try:
        llm = _get_llm()
        data_url = image_to_data_url(image_path)
        messages = [
            HumanMessage(
                content=[
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": "你是一位文字提取专家，请将图片中的文字提取成LaTex格式的文本，请只输出提取后的文本，不要改动文本内容，也不要输出任何其余内容"}
                ]
            )
        ]
        response = llm.invoke(messages)
        return str(response.content or "")
    except Exception:
        return ""

def extract_question_from_image(image_path: str) -> str:
    try:
        llm = _get_llm()
        data_url = image_to_data_url(image_path)
        messages = [
            HumanMessage(
                content=[
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": r"""
你是一位文字提取专家。请从图片中提取数学题目的题干、选项（如有）、答案和解析。

【严格输出要求】
1. 输出为 txt 格式，不要使用 Markdown，不要使用符号如：*, #, -, ``` 等。
2. 禁止出现**题号**，例如 “1.” “（1）” “1、” 等一切题目前缀编号；禁止出现任何来源/出处，例如年份、课标 I/II、全国卷、地方卷、学校名称等。
3. 每道题输出**恰好两行**：
   第 1 行：题目 + 选项（若有）
   第 2 行：答案（只输出答案本身，不包括“答案”两个字） + 解析
   ——（注意）第1行与第2行之间**绝对不要**使用 "||" 或其它分隔符；也不要在两行之间留空行。
4. 题目中：
   - 题目与选项之间用 "||" 分割
   - 各选项之间也用 "||" 分割
   - 多选题题干最前加 "(多选)"
5. 如果题干、选项、小问、解析中出现原始换行（包括：题干中的段落换行、一个小问到下一个小问的换行、解析内部的换行），必须使用 "||" 替代换行。
   ——规则重点：原文本中只要有换行，就必须输出 "||"，不能漏。
6. 如果原图没有解析，请你自动补全一个合理的解析。
7. 输出中只能包含题目内容，不要包含示例。
8. 所有数学表达式、公式、符号，一律用“$...$”包裹，包括填空题答案中的数字
                """}
                ]
            )
        ]
        response = llm.invoke(messages)
        return str(response.content or "")
    except Exception:
        return ""
