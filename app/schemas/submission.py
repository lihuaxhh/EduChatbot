from pydantic import BaseModel
from typing import List

class AnswerCreate(BaseModel):
    question_id: int
    student_answer: str
    image_path: str | None = None

class SubmissionCreate(BaseModel):
    assignment_id: int
    student_id: int
    answers: List[AnswerCreate]
