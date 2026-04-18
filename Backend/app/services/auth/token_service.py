from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from app.config import get_settings
from app.db.models.user import User

settings = get_settings()


async def verify_access_token(access_token: str):
    try:
        payload = jwt.decode(access_token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")
        user_id = payload.get("sub")

        if user_id is None:
            raise Exception("Invalid token or expired token")
        return user_id

    except JWTError:
        raise JWTError("Token in invalid or expired")


async def verify_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")
        user_id = payload.get("sub")
        if user_id is None:
            raise Exception("Invalid token or expired token")
        return user_id
    except JWTError:
        raise JWTError("Refresh token in invalid or expired")


async def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
        return payload
    except JWTError:
        return JWTError("Invalid token or expired token")


async def get_current_user(db: AsyncSession, token: str):
    try:
        payload = await jwt.decode(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise JWTError("User not found")
        return user
    except JWTError:
        return JWTError("Invalid token or expired token")
