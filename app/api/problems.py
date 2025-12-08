#app\api\problems.py
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..services.load_questions import upload_questions
from fastapi import APIRouter, Depends, HTTPException
from ..crud.question import get_question_by_id
from ..services.recommendation import search_by_slot
from ..schemas.recommendation import RecommendationRequest, RecommendationResponse, RecommendedItem
from ..crud.question import has_wrong_submission

router = APIRouter(prefix="/problems", tags=["Problems"])

@router.post("/upload")
def upload_question_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    teacher_id = 1  # 先写死，后续再接入登录系统
    result = upload_questions(file, db, teacher_id)
    return result

@router.post("/{problem_id}/recommendation", response_model=RecommendationResponse)
def recommend_questions(req: RecommendationRequest, db: Session = Depends(get_db)):
    question = get_question_by_id(db, req.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if not has_wrong_submission(db, req.student_id, req.question_id):
        raise HTTPException(status_code=400, detail="Only incorrect submissions are eligible for recommendation")
    final = search_by_slot(db, req.student_id, req.question_id, req.slot, req.expect_num)
    return RecommendationResponse(
        base_question_id=req.question_id,
        slot=req.slot,
        expected=req.expect_num,
        found=len(final),
        items=[RecommendedItem(id=qid, score=score) for qid, score in final]
    )

