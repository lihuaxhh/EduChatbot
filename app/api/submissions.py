# api/submissions.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import tempfile
import uuid
import pathlib
from typing import List
from ..ml.ocr import extract_answer_from_image
from ..schemas.submission import SubmissionCreate
from ..crud.submission import create_submissions
from ..db.session import get_db
from ..services.correction import grade_answer_service
from ..crud.question import get_question_by_id
from ..models.question import StudentSubmission, ErrorAnalysis
from pydantic import BaseModel

router = APIRouter(prefix="/submissions", tags=["Submissions"])

STATIC_DIR = pathlib.Path(__file__).parent.parent / "static" / "submissions"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

class SubmissionResultResponse(BaseModel):
    question_id: int
    student_answer: str
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
    
    # Trigger background correction
    background_tasks.add_task(run_batch_correction, sub, db)
    
    return {"status": "ok", "submitted_count": count}

def run_batch_correction(sub: SubmissionCreate, db: Session):
    # Note: In a real async background task, you might need a new DB session if the dependency injected one is closed.
    from ..db.session import SessionLocal
    local_db = SessionLocal()
    try:
        for ans in sub.answers:
            # Check if answer is an image path
            student_text = ans.student_answer
            if student_text.startswith("[IMAGE]"):
                image_path = student_text.replace("[IMAGE]", "")
                try:
                    # image_path might be a URL or relative path.
                    # We stored it as relative path "static/submissions/..."
                    # We need absolute path for OCR
                    abs_path = os.path.abspath(os.path.join(os.getcwd(), "app", image_path))
                    if os.path.exists(abs_path):
                        ocr_text = extract_answer_from_image(abs_path)
                        student_text = ocr_text or "[无法识别图片内容]"
                        
                        # Update student answer in DB with OCR result so we can see what was graded
                        submission_record = local_db.query(StudentSubmission).filter(
                            StudentSubmission.student_id == sub.student_id,
                            StudentSubmission.assignment_id == sub.assignment_id,
                            StudentSubmission.question_id == ans.question_id
                        ).first()
                        if submission_record:
                            # Append OCR text to image path for record
                            submission_record.student_answer = f"{ans.student_answer}\n[OCR]: {student_text}"
                            local_db.commit()
                            
                    else:
                        student_text = "[图片文件未找到]"
                except Exception as e:
                    print(f"OCR Error for {image_path}: {e}")
                    student_text = "[OCR处理失败]"
            
            # Now grade
            try:
                # Grade
                result = grade_answer_service(ans.question_id, student_text, local_db)
                
                # Update Submission
                submission_record = local_db.query(StudentSubmission).filter(
                    StudentSubmission.student_id == sub.student_id,
                    StudentSubmission.assignment_id == sub.assignment_id,
                    StudentSubmission.question_id == ans.question_id
                ).first()
                
                if submission_record:
                    # Update is_correct
                    is_correct = result.is_correct
                    submission_record.is_correct = is_correct
                    
                    # Update or Create ErrorAnalysis
                    # If incorrect, create ErrorAnalysis
                    if not is_correct:
                        # Check if exists
                        ea = local_db.query(ErrorAnalysis).filter(ErrorAnalysis.submission_id == submission_record.id).first()
                        if not ea:
                            ea = ErrorAnalysis(submission_id=submission_record.id)
                            local_db.add(ea)
                        
                        ea.error_type = result.error_type
                        ea.analysis = result.analysis
                    
                    local_db.commit()

            except Exception as e:
                print(f"Grading failed for Q{ans.question_id}: {e}")
                local_db.rollback()
    finally:
        local_db.close()

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
