import os
import sys
CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User, Student
from app.models.question import Question, StudentSubmission

def seed_user_and_wrong_submissions():
    db = SessionLocal()
    try:
        phone = "18000000000"
        user = db.query(User).filter(User.phone == phone).first()
        if not user:
            user = User(phone=phone, password_hash="test", role="student", is_active=True)
            db.add(user)
            db.commit()
            db.refresh(user)
        student = db.query(Student).filter(Student.user_id == user.id).first()
        if not student:
            student = Student(user_id=user.id, student_number="S0001", name="Test Student")
            db.add(student)
            db.commit()
            db.refresh(student)
        questions = db.query(Question).order_by(Question.id).limit(5).all()
        qids = [q.id for q in questions]
        inserted = 0
        for q in questions:
            exists = db.query(StudentSubmission.id).filter(
                StudentSubmission.student_id == student.id,
                StudentSubmission.question_id == q.id
            ).first()
            if exists:
                continue
            sub = StudentSubmission(
                question_id=q.id,
                student_id=student.id,
                student_answer="wrong",
                is_correct=False
            )
            db.add(sub)
            inserted += 1
        db.commit()
        return student.id, qids, inserted
    finally:
        db.close()

def pick_non_wrong_question(student_id):
    db = SessionLocal()
    try:
        wrong_qids = {r[0] for r in db.query(StudentSubmission.question_id).filter(
            StudentSubmission.student_id == student_id,
            StudentSubmission.is_correct.is_(False)
        ).all()}
        candidate = db.query(Question.id).filter(~Question.id.in_(wrong_qids)).order_by(Question.id).first()
        return candidate[0] if candidate else None
    finally:
        db.close()

def test_recommendation_for_wrong_only():
    student_id, qids, inserted = seed_user_and_wrong_submissions()
    base_qid = qids[0] if qids else None
    if not base_qid:
        print("no questions available")
        return
    client = TestClient(app)
    payload = {
        "question_id": base_qid,
        "student_id": student_id,
        "slot": "high",
        "expect_num": 5
    }
    resp = client.post(f"/api/problems/{base_qid}/recommendation", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["base_question_id"] == base_qid
    assert isinstance(data["items"], list)
    print("recommendation items count:", data["found"]) 

def test_recommendation_reject_without_wrong():
    student_id, qids, inserted = seed_user_and_wrong_submissions()
    other_qid = pick_non_wrong_question(student_id)
    if not other_qid:
        print("no non-wrong question available, skip")
        return
    client = TestClient(app)
    payload = {
        "question_id": other_qid,
        "student_id": student_id,
        "slot": "high",
        "expect_num": 5
    }
    resp = client.post(f"/api/problems/{other_qid}/recommendation", json=payload)
    assert resp.status_code == 400, resp.text

def print_recommendations_for_wrong_set():
    student_id, qids, inserted = seed_user_and_wrong_submissions()
    client = TestClient(app)
    db = SessionLocal()
    try:
        for base_qid in qids:
            payload = {
                "question_id": base_qid,
                "student_id": student_id,
                "slot": "high",
                "expect_num": 5
            }
            resp = client.post(f"/api/problems/{base_qid}/recommendation", json=payload)
            if resp.status_code != 200:
                print("base", base_qid, "status", resp.status_code)
                continue
            data = resp.json()
            ids = [it["id"] for it in data.get("items", [])]
            rows = db.query(Question.id, Question.question).filter(Question.id.in_(ids)).all() if ids else []
            mapping = {row[0]: row[1] for row in rows}
            base_row = db.query(Question.question).filter(Question.id == base_qid).first()
            base_text = base_row[0] if base_row else ""
            print("base_id", base_qid)
            print("base_text", base_text)
            for it in data.get("items", []):
                qtext = mapping.get(it["id"], "")
                print("rec_id", it["id"], "score", it["score"], "text", qtext)
    finally:
        db.close()

if __name__ == "__main__":
    test_recommendation_for_wrong_only()
    test_recommendation_reject_without_wrong()
    print_recommendations_for_wrong_set()
