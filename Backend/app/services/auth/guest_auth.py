from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.db.models.user import User
from app.services.auth.email_auth import create_access_token, create_refresh_token


async def create_guest_user(db: AsyncSession, fingerprint: str):
    result = await db.execute(
        select(User).where(User.device_fingerprint == fingerprint)
    )
    existing = result.scalar_one_or_none()

    if existing:
        if existing.queries_today >= 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guest limit reached. Please sign up to continue.",
            )
        return {
            "user": existing,
            "access_token": create_access_token(existing.id),
            "refresh_token": create_refresh_token(existing.id),
        }

    user = User(
        auth_provider="guest",
        is_active=True,
        plan="free",
        device_fingerprint=fingerprint,
        queries_today=0,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "user": user,
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
    }
