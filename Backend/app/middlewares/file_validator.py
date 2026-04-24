from fastapi import Depends, HTTPException, UploadFile, status
from app.db.models.user import User

from app.middlewares.auth_middleware import get_current_user
import os
import logging

logger = logging.getLogger(__name__)

LIMITS = {
    "free": 3 * 1024 * 1024,
    "pro": 10 * 1024 * 1024,
}

ALLOWED_TYPES = [
    "text/csv",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]

ALLOWED_EXT = [".csv", ".pdf", ".xlsx"]


async def validate_file_upload(
    file: UploadFile,
    user: User = Depends(get_current_user),
):
    if user.auth_provider == "guest":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot upload files. Please sign up.",
        )

    limit = LIMITS.get(user.plan)

    if limit is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid plan",
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid file type",
        )

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only CSV, PDF and Excel files allowed",
        )

    contents = await file.read()
    file_size = len(contents)

    await file.seek(0)

    if file_size > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max allowed: {limit // (1024*1024)} MB",
        )

    return file
