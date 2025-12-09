from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QuestionBase(BaseModel):
    question: str
    difficulty_tag: str
    knowledge_tag: str

class QuestionRead(QuestionBase):
    id: int
    normalized_question: str
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True
