from app.crud.question import get_question_by_id, get_candidate_knowledge_nodes
from app.ml.correction import grading_logic, identify_knowledge_from_candidates
from sqlalchemy.orm import Session
from app.schemas.correction import ErrorType
import json


def grade_answer_service(question_id: int, student_answer: str, db: Session):
    question = get_question_by_id(db, question_id)
    tag = question.knowledge_tag or {}
    if isinstance(tag, str):
        try:
            tag = json.loads(tag)
        except Exception:
            tag = {}
    function_types = tag.get("types") or tag.get("function_types") or []
    function_properties = tag.get("properties") or tag.get("function_properties") or []

    result = grading_logic(
        question.question,
        student_answer,
        question.answer
    )
    print(result)
    if (not result["is_correct"]
            and result["error_type"] == "knowledge"
            and (function_types or function_properties)):
        print("function_types:", function_types)
        print("function_properties:", function_properties)
        candidates = get_candidate_knowledge_nodes(db, function_types, function_properties)
        for candidate in candidates:
            print("candidate.name:", candidate.name)
        knowledge_id = identify_knowledge_from_candidates(
            question=question.question,
            student_answer=student_answer,
            correct_answer=question.answer,
            candidates=candidates
        )
        print(f"知识点 ID: {knowledge_id}")

    return result
