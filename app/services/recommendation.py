from faiss_service import FaissService
from ..crud.question import get_done_questions, get_difficulty
from sqlalchemy.orm import Session

def search_by_slot(db: Session, student_id: int, question_id: int, slot="high", expect_num=5):
    slot_ranges = {
        "high": (0.9, 1.0),
        "mid": (0.75, 0.9),
        "low": (0.5, 0.75)
    }
    allowed_difficulties_range = {
        "易": ["易", "中"],
        "中": ["中", "难"],
        "难": ["难"]
    }
    left, right = slot_ranges[slot]
    done_set = get_done_questions(db, student_id)
    current_difficulty = get_difficulty(db, question_id)
    allowed_difficulties = allowed_difficulties_range[current_difficulty]

    faiss_service = FaissService(dim=768)
    index_size = faiss_service.index.ntotal
    vector = faiss_service.get_vector_by_id(question_id)
    k = 20
    difficulty_cache = {}
    while True:
        ids, scores = faiss_service.search_vector(vector, k=k)
        candidates = []
        for qid, score in zip(ids, scores):
            # 相似度过滤
            if not (left <= score <= right):
                continue
            # 学生是否做过
            if qid in done_set:
                continue
            # 难度是否符合
            if qid in difficulty_cache:
                q_difficulty = difficulty_cache.get(qid)
            else:
                q_difficulty = get_difficulty(db, qid)
                difficulty_cache[qid] = q_difficulty
            if q_difficulty not in allowed_difficulties:
                continue
            candidates.append((qid, score))

        if len(candidates) >= expect_num:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[:expect_num]
        if k >= index_size:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates
        k = min(k * 2, index_size)
