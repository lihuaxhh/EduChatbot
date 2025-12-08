# test_local_models.py
from app.ml.classify_questions_from_teachers import build_bert
from app.services.embedding_service import EmbeddingService

# 测试 BERT
tokenizer, bert = build_bert()
print("BERT 已加载")

# 测试 text2vec
emb = EmbeddingService()
vec = emb.encode(["你好，这是测试"])
print("text2vec 向量形状:", vec.shape)