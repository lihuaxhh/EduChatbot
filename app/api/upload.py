from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid
from pathlib import Path

router = APIRouter()

# Define upload directory relative to app root
# app/static/avatars
UPLOAD_DIR = Path(__file__).parent.parent / "static" / "avatars"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {e}")
        
    # Return the URL relative to server root
    # Static files are mounted at /static
    return {"url": f"http://127.0.0.1:8000/static/avatars/{filename}"}
