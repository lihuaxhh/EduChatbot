from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from ..crud.clazz import get_classes_by_teachers
from app.models.user import User
from .deps import get_current_active_teacher

router = APIRouter(prefix="/teacher", tags=["Teacher"])

@router.get("/classes")
def get_teacher_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_teacher)
):
    return get_classes_by_teachers(db, current_user.teacher.id)
