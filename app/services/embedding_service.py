# app/services/embedding_service.py
import os
import json
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self):
        # 获取当前文件所在目录（app/services/）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建指向 app/run_models/text2vec-base-chinese 的路径
        model_path = os.path.join(current_dir, "..", "run_models", "text2vec-base-chinese")

        print("正在加载本地 text2vec 模型...")
        self.model = SentenceTransformer(model_path)
        print("✅ text2vec 模型加载完成")

    def build_text(self, questions):
        texts = []
        for q in questions:
            if hasattr(q, 'knowledge_tag'):
                tag = q.knowledge_tag
                if isinstance(tag, str):
                    try:
                        tag = json.loads(tag)
                    except Exception:
                        tag = {}
                types = tag.get("types") or tag.get("function_types") or []
                properties = tag.get("properties") or tag.get("function_properties") or []
            else:
                types = q.types
                properties = q.properties
            parts = []
            parts.append(f"[函数类型：{types}]")
            parts.append(f"[函数性质：{properties}]")
            parts.append(q.question)
            texts.append(" ".join(parts))
        return texts

    def encode(self, questions):
        texts = self.build_text(questions)
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings
