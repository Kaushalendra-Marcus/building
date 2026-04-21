from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest
from app.services.auth.email_auth import register_user, login_user
from app.services.auth.guest_auth import create_guest_user
from app.services.auth.google_auth import google_login
from app.services.auth.email_verification import verify_email_token
from app.schemas.auth import GuestAuthRequest
from app.schemas.auth import GoogleAuthRequest
from app.schemas.auth import TokenResponse
from sqlalchemy import select
from uuid import UUID

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=TokenResponse)
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await register_user(db, data.email, data.password, data.name)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/signin", response_model=TokenResponse)
async def signin(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await login_user(db, data.email, data.password)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/guest")
async def guest(data: GuestAuthRequest, db: AsyncSession = Depends(get_db)):
    return await create_guest_user(db, data.device_id)


@router.post("/google")
async def google(data: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    return await google_login(db, data.token)


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    user_id = UUID(verify_email_token(token))
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.is_email_verified = True
    await db.commit()
    await db.refresh(user)

    return {"message": "Email verified successfully"}
