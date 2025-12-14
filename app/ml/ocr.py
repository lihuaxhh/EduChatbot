from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import base64
import os
import json
import re

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

def extract_blocks_from_image(image_path: str):
    """
    将整页图片按题号切分为多个块，返回 [{\"question_no\": int|null, \"text\": str}]
    题号识别示例：1. 1、(1) 第1题 等，统一解析为数字
    """
    try:
        llm = _get_llm()
        data_url = image_to_data_url(image_path)
        messages = [
            HumanMessage(
                content=[
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": r"""
你是一位版面分析与文字提取专家。请从这张图片中识别学生的作答内容，并按题号进行切分。

【任务要求】
1) 学生通常用如下格式标注题号： "1." "1、" "(1)" "第1题"；可能有中文数字。
2) 请按题号顺序切分整页，每个题块只包含该题的学生作答文本（不需要题干）。
3) 输出 JSON 数组，元素为：
   { "question_no": number|null, "text": string }
   - question_no：尽量解析为阿拉伯数字（如 '一'→1），无法判断则为 null
   - text：该题的作答文本，保留数学表达式与符号（使用 $...$ 包裹）
4) 只输出 JSON，不要任何解释或其它文本。
                """}
                ]
            )
        ]
        response = llm.invoke(messages)
        raw = str(response.content or "[]")
        try:
            data = json.loads(raw)
            if isinstance(data, list) and len(data) > 0:
                # 归一化字段
                result = []
                for item in data:
                    qno = item.get("question_no", None)
                    # 将中文数字简单映射到整数
                    if isinstance(qno, str):
                        cn_map = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10}
                        qno = cn_map.get(qno.strip(), None)
                    result.append({"question_no": qno if isinstance(qno, int) else None, "text": str(item.get("text","")).strip()})
                if result:
                    return result
        except Exception:
            pass
        # Fallback: 提取整页文本后用题号正则切分
        text_all = extract_answer_from_image(image_path) or ""
        text_all = text_all.strip()
        if not text_all:
            return []
        # 题号正则：第X题、阿拉伯数字、括号数字
        pattern = re.compile(r'(?m)^\s*(?:第\s*([一二三四五六七八九十]+)\s*题|([0-9]+)[\.\、)]|\(([0-9]+)\))\s*')
        blocks = []
        indices = []
        for m in pattern.finditer(text_all):
            indices.append((m.start(), m.end(), m.group(1), m.group(2), m.group(3)))
        if not indices:
            # 若行首未匹配，尝试用简单行号分割
            lines = text_all.splitlines()
            cur_no = None
            cur_buf = []
            for ln in lines:
                m = re.match(r'^\s*([0-9]+)\s*[\.、)]\s*(.*)$', ln)
                if m:
                    # flush previous
                    if cur_buf:
                        blocks.append({"question_no": cur_no, "text": "\n".join(cur_buf).strip()})
                        cur_buf = []
                    cur_no = int(m.group(1))
                    rest = m.group(2).strip()
                    if rest:
                        cur_buf.append(rest)
                else:
                    cur_buf.append(ln)
            if cur_buf:
                blocks.append({"question_no": cur_no, "text": "\n".join(cur_buf).strip()})
            return [b for b in blocks if (b["question_no"] is not None and b["text"])]
        # 有匹配时按位置切分
        for i in range(len(indices)):
            start = indices[i][1]
            end = indices[i+1][0] if i+1 < len(indices) else len(text_all)
            seg = text_all[start:end].strip()
            cn = indices[i][2]
            arabic = indices[i][3] or indices[i][4]
            qno = None
            if arabic:
                try:
                    qno = int(arabic)
                except Exception:
                    qno = None
            elif cn:
                cn_map = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10}
                qno = cn_map.get(cn.strip(), None)
            if seg:
                blocks.append({"question_no": qno, "text": seg})
        return [b for b in blocks if (b["question_no"] is not None and b["text"])]
    except Exception:
        return []

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
