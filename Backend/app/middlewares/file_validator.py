from fastapi import Depends, HTTPException, UploadFile, status
from app.db.models.user import User

from app.middlewares.auth_middleware import get_current_user

LIMITS = {
    "free": 1 * 1024 * 1024,
    "pro": 5 * 1024 * 1024,
}


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

    contents = await file.read()
    file_size = len(contents)

    await file.seek(0)

    if file_size > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max allowed: {limit // (1024*1024)} MB",
        )

    return file
