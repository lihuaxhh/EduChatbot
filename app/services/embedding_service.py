from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('shibing624/text2vec-base-chinese')

    def build_text(self, questions):
        texts = []
        for question in questions:
            parts = []
            parts.append(f"[函数类型：{question.knowledge_tag["types"]}]")
            parts.append(f"[函数性质：{question.knowledge_tag["properties"]}]")
            parts.append(question.question)
            texts.append(" ".join(parts))
        return texts

    def encode(self, questions):
        texts = self.build_text(questions)
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings