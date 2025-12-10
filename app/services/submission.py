from typing import List, Dict, Any
import os
import pathlib
from sqlalchemy.orm import Session
from app.schemas.submission import SubmissionCreate
from app.models.question import StudentSubmission, ErrorAnalysis
from app.services.correction import grade_answer_service
from app.ml.ocr import extract_answer_from_image

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
STATIC_SUB_DIR = APP_ROOT / "static" / "submissions"

def _resolve_abs_image_path(img_path: str) -> str:
    p = pathlib.Path(img_path)
    if p.is_absolute():
        return str(p)
    return str(APP_ROOT / img_path)

def process_submission(sub: SubmissionCreate, db: Session) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for ans in sub.answers:
        student_text = ans.student_answer or ""
        img_path = getattr(ans, "image_path", None)
        if not img_path and isinstance(student_text, str) and student_text.startswith("[IMAGE]"):
            img_path = student_text.replace("[IMAGE]", "")
        if img_path:
            abs_path = _resolve_abs_image_path(img_path)
            if os.path.exists(abs_path):
                try:
                    ocr_text = extract_answer_from_image(abs_path)
                    student_text = ocr_text or ""
                except Exception:
                    student_text = "[OCR处理失败]"
            else:
                student_text = "[图片文件未找到]"
        try:
            result = grade_answer_service(ans.question_id, student_text, db)
        except Exception:
            result = None
        submission_record = db.query(StudentSubmission).filter(
            StudentSubmission.student_id == sub.student_id,
            StudentSubmission.assignment_id == sub.assignment_id,
            StudentSubmission.question_id == ans.question_id
        ).first()
        if submission_record:
            if img_path:
                submission_record.image_path = img_path
            submission_record.student_answer = student_text if student_text else "[OCR未识别内容]"
            if result is not None:
                is_correct = result.is_correct
                submission_record.is_correct = is_correct
                if not is_correct:
                    ea = db.query(ErrorAnalysis).filter(ErrorAnalysis.submission_id == submission_record.id).first()
                    if not ea:
                        ea = ErrorAnalysis(submission_id=submission_record.id)
                        db.add(ea)
                    ea.error_type = result.error_type
                    ea.analysis = result.analysis
            db.commit()
            results.append({
                "question_id": ans.question_id,
                "student_answer": submission_record.student_answer,
                "image_path": submission_record.image_path,
                "is_correct": bool(submission_record.is_correct) if submission_record.is_correct is not None else False,
                "error_type": submission_record.error_analysis.error_type if (submission_record.error_analysis and submission_record.is_correct is False) else None,
                "analysis": submission_record.error_analysis.analysis if (submission_record.error_analysis and submission_record.is_correct is False) else None
            })
    return results
