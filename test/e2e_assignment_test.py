import os
import sys
import pathlib
import random
from sqlalchemy import text

# Setup path
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.question import Question, Assignment, StudentSubmission, ErrorAnalysis

def main():
    db = SessionLocal()
    try:
        print("=== E2E Test: Assignment 10, Question 2 ===")

        # 1. Ensure Question 2 exists
        q2 = db.query(Question).filter(Question.id == 2).first()
        if not q2:
            print("Question 2 not found. Creating mock question...")
            q2 = Question(
                id=2,
                question="求函数 $f(x) = \log_2(x+1)$ 的定义域。",
                normalized_question="求函数f(x)=log_2(x+1)的定义域",
                answer="(-1, +\infty)",
                knowledge_tag='{"types": ["对数函数"], "properties": ["定义域"]}',
                difficulty_tag="easy"
            )
            db.add(q2)
            db.commit()
        print(f"✅ Question 2 ready: {q2.question}")

        # 2. Ensure Assignment 10 exists
        assign = db.query(Assignment).filter(Assignment.id == 10).first()
        if not assign:
            print("Assignment 10 not found. Creating...")
            assign = Assignment(
                id=10,
                title="E2E Test Assignment",
                teacher_id=1,
                class_id=1,
                assigned_student_ids=[1],
                assigned_question_ids=[2]
            )
            db.add(assign)
        else:
            print("Assignment 10 exists. Updating question list...")
            assign.assigned_question_ids = [2]
            assign.assigned_student_ids = [1]
        
        db.commit()
        print(f"✅ Assignment 10 ready: {assign.title}")

        # 3. Select an image
        static_dir = BASE_DIR / "app" / "static" / "submissions"
        images = list(static_dir.glob("*.jpg")) + list(static_dir.glob("*.png"))
        if not images:
            print("❌ No images found in app/static/submissions")
            return
        
        # Pick one image (e.g., the first one)
        selected_img = images[0]
        # Relative path for API
        rel_path = f"static/submissions/{selected_img.name}"
        print(f"📸 Selected image: {rel_path}")

        # 4. Submit via TestClient
        client = TestClient(app)
        payload = {
            "assignment_id": 10,
            "student_id": 1,
            "answers": [
                {
                    "question_id": 2,
                    "student_answer": rel_path
                }
            ]
        }
        
        print("\n🚀 Submitting assignment...")
        resp = client.post("/api/submissions/", json=payload)
        if resp.status_code != 200:
            print(f"❌ Submission failed: {resp.text}")
            return
        print(f"✅ Submission successful: {resp.json()}")

        # 5. Verify Database
        print("\n🔍 Verifying Database Records...")
        # Need to expire/refresh to see updates
        db.expire_all()
        
        sub = db.query(StudentSubmission).filter(
            StudentSubmission.assignment_id == 10,
            StudentSubmission.student_id == 1,
            StudentSubmission.question_id == 2
        ).first()

        if not sub:
            print("❌ Submission record not found in DB!")
            return

        print(f"  [Record ID]: {sub.id}")
        print(f"  [Image Path]: {sub.image_path}")
        print(f"  [Student Answer (OCR)]: {sub.student_answer}")
        print(f"  [Is Correct]: {sub.is_correct}")
        
        if sub.error_analysis:
            print(f"  [Error Type]: {sub.error_analysis.error_type}")
            print(f"  [Analysis]: {sub.error_analysis.analysis}")
        else:
            print("  [Analysis]: No error analysis (Correct answer?)")

    finally:
        db.close()

if __name__ == "__main__":
    main()
