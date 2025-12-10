import os
import sys
import pathlib
import argparse
from dotenv import load_dotenv

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db.session import SessionLocal
from app.services.correction import grade_answer_service

def main():
    load_dotenv()
    os.environ.setdefault('OPENAI_API_KEY', os.getenv('DASHSCOPE_API_KEY', ''))
    if os.getenv('DASHSCOPE_BASE_URL'):
        os.environ.setdefault('OPENAI_BASE_URL', os.getenv('DASHSCOPE_BASE_URL'))

    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, default='')
    parser.add_argument('--question-id', type=int, default=0)
    args = parser.parse_args()

    from app.ml.ocr import extract_answer_from_image
    db = SessionLocal()
    try:
        image_path = args.image
        if not image_path:
            static_dir = BASE_DIR / 'app' / 'static' / 'submissions'
            candidates = []
            if static_dir.exists():
                for p in static_dir.iterdir():
                    if p.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                        candidates.append(str(p))
            image_path = candidates[0] if candidates else ''
        if not image_path or not os.path.exists(image_path):
            print('Image not found')
            return

        print('[OCR] extracting...')
        text = extract_answer_from_image(image_path)
        print('[OCR] text:', text)

        if args.question_id:
            result = grade_answer_service(args.question_id, text, db)
            print('[Grade] is_correct:', result.is_correct)
            print('[Grade] message:', result.message)
            print('[Grade] error_type:', result.error_type)
            print('[Grade] analysis:', result.analysis)
    finally:
        db.close()

if __name__ == '__main__':
    main()
