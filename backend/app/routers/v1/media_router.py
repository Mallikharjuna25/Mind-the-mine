import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from backend.app.core.config import settings
from backend.app.core.security import get_current_user

router = APIRouter(prefix="/media", tags=["Media Evidence"])

@router.post("/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")

    return {
        "filename": unique_filename,
        "url": f"/storage/uploads/{unique_filename}",
        "size_bytes": len(contents),
        "content_type": file.content_type
    }
