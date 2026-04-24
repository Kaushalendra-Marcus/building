from fastapi import Depends, HTTPException, status

from app.db.models.user import User
from app.middlewares.auth_middleware import get_current_user


def plan_checker(user_plan: str):
    async def checker(user: User = Depends(get_current_user)):
        required_plan = user.plan
        hierarchy = {
            "guest": 0,
            "free": 1,
            "pro": 2,
        }
        if hierarchy.get(user_plan, 0) < hierarchy.get(required_plan, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_plan} plan required",
            )

        return user

    return checker
