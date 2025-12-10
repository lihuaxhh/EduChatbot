from sqlalchemy.orm import Session
from app.models.question import StudentSubmission
from app.schemas.submission import SubmissionCreate

def create_submissions(db: Session, sub: SubmissionCreate):
    objects = []
    # Delete existing submissions for this student/assignment to allow re-submission?
    # Or just add. Let's delete previous ones for this assignment/student to avoid duplicates.
    db.query(StudentSubmission).filter(
        StudentSubmission.assignment_id == sub.assignment_id,
        StudentSubmission.student_id == sub.student_id
    ).delete()
    
    for ans in sub.answers:
        img = None
        if getattr(ans, "image_path", None):
            img = ans.image_path
        else:
            if isinstance(ans.student_answer, str) and ans.student_answer.startswith("[IMAGE]"):
                img = ans.student_answer.replace("[IMAGE]", "")
        initial_answer = ans.student_answer
        if img:
            initial_answer = ""
        obj = StudentSubmission(
            assignment_id=sub.assignment_id,
            student_id=sub.student_id,
            question_id=ans.question_id,
            student_answer=initial_answer,
            image_path=img
        )
        objects.append(obj)
    db.add_all(objects)
    db.commit()
    return len(objects)
