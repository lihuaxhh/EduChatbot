import sys
import pathlib
import os

# Ensure app directory is in path
APP_DIR = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(APP_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.user import User, Teacher, Student, Class
from core.security import get_password_hash

def seed_test_data():
    print(f"Connecting to database: {settings.database_url}")
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 1. Create Teacher
        teacher_user = db.query(User).filter(User.username == "teacher1").first()
        if not teacher_user:
            teacher_user = User(
                username="teacher1",
                password_hash=get_password_hash("123456"),
                role="teacher",
                nickname="张老师",
                is_active=True
            )
            db.add(teacher_user)
            db.commit()
            db.refresh(teacher_user)
            
            teacher_profile = Teacher(user_id=teacher_user.id, name="张伟")
            db.add(teacher_profile)
            db.commit()
            db.refresh(teacher_profile)
            print("✅ 测试教师已创建: teacher1 / 123456")
        else:
            teacher_profile = teacher_user.teacher
            print("ℹ️ 测试教师已存在")

        # 2. Create Class
        clazz = db.query(Class).filter(Class.name == "三年二班").first()
        if not clazz:
            clazz = Class(name="三年二班", teacher_id=teacher_profile.id)
            db.add(clazz)
            db.commit()
            db.refresh(clazz)
            print("✅ 测试班级已创建: 三年二班")
        else:
            print("ℹ️ 测试班级已存在")
        
        # 3. Create Student
        student_user = db.query(User).filter(User.username == "student1").first()
        if not student_user:
            student_user = User(
                username="student1",
                password_hash=get_password_hash("123456"),
                role="student",
                nickname="小明",
                is_active=True
            )
            db.add(student_user)
            db.commit()
            db.refresh(student_user)

            student_profile = Student(
                user_id=student_user.id, 
                name="王明", 
                student_number="S2024001", 
                class_id=clazz.id
            )
            db.add(student_profile)
            db.commit()
            print("✅ 测试学生已创建: student1 / 123456")
        else:
            print("ℹ️ 测试学生已存在")

    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_data()
