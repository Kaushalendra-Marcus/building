from fastapi import Depends, HTTPException, status

from app.db.models.user import User
from app.middlewares.auth_middleware import get_current_user

def plan_checker(required_plan: str):
    async def checker(user: User = Depends(get_current_user)):
        hierarchy = {"guest": 0, "free": 1, "pro": 2}

        user_level = hierarchy.get(user.plan, 0)
        required_level = hierarchy.get(required_plan, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_plan} plan required"
            )
        return user

    return checker
