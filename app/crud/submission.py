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
        obj = StudentSubmission(
            assignment_id=sub.assignment_id,
            student_id=sub.student_id,
            question_id=ans.question_id,
            student_answer=ans.student_answer
        )
        objects.append(obj)
    db.add_all(objects)
    db.commit()
    return len(objects)
