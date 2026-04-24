from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.db.database import get_db
from app.db.models.user import User
from app.middlewares.auth_middleware import get_current_user

LIMITS = {"guest": 2, "free": 4, "pro": 40}


async def rate_limiter(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    now = datetime.now(timezone.utc)
    if user.last_reset.date() != now.date():
        user.queries_today = 0
        last_reset = user.last_reset
        if last_reset.tzinfo is None:
            last_reset = last_reset.replace(tzinfo=timezone.utc)
        user.last_reset = now
        await db.commit()

    if user.auth_provider == "guest":
        limit = LIMITS["guest"]
    else:
        limit = LIMITS.get(user.plan, LIMITS["free"])

    if user.queries_today >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily limit reached. Upgrade your plan.",
        )

    user.queries_today += 1
    await db.commit()

    return user
