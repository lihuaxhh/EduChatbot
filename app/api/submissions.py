# api/submissions.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import tempfile
import uuid
import pathlib
from typing import List
from ..schemas.submission import SubmissionCreate
from ..ml.ocr import extract_answer_from_image, extract_blocks_from_image
from ..crud.submission import create_submissions
from ..db.session import get_db
from ..models.question import StudentSubmission, ErrorAnalysis
from ..services.submission import process_submission
from pydantic import BaseModel

router = APIRouter(prefix="/submissions", tags=["Submissions"])

STATIC_DIR = pathlib.Path(__file__).parent.parent / "static" / "submissions"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

class SubmissionResultResponse(BaseModel):
    question_id: int
    student_answer: str
    image_path: str | None = None
    is_correct: bool
    error_type: str = None
    analysis: str = None

@router.get("/results", response_model=List[SubmissionResultResponse])
def get_submission_results(assignment_id: int, student_id: int, db: Session = Depends(get_db)):
    submissions = db.query(StudentSubmission).filter(
        StudentSubmission.assignment_id == assignment_id,
        StudentSubmission.student_id == student_id
    ).all()
    
    results = []
    for sub in submissions:
        res = SubmissionResultResponse(
            question_id=sub.question_id,
            student_answer=sub.student_answer,
            image_path=sub.image_path,
            is_correct=sub.is_correct if sub.is_correct is not None else False
        )
        if sub.is_correct is False and sub.error_analysis:
            res.error_type = sub.error_analysis.error_type
            res.analysis = sub.error_analysis.analysis
        results.append(res)
    return results

@router.post("/")
def submit_assignment(sub: SubmissionCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    count = create_submissions(db, sub)
    results = process_submission(sub, db)
    return {"status": "ok", "submitted_count": count, "results": results}

@router.post("/upload_image")
async def upload_submission_image(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Only images allowed")
    
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = STATIC_DIR / filename
    
    with open(filepath, "wb") as f:
        f.write(await file.read())
        
    # Return relative path for storage
    return {"path": f"static/submissions/{filename}", "url": f"/static/submissions/{filename}"}

@router.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Only PNG/JPG images are allowed.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        extracted_text = extract_answer_from_image(tmp_path)
        return JSONResponse({"text": extracted_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@router.post("/ocr_split")
async def ocr_split_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Only PNG/JPG images are allowed.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        blocks = extract_blocks_from_image(tmp_path)
        return JSONResponse({"blocks": blocks})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR split failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
