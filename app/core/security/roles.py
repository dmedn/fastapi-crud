from fastapi import Depends, HTTPException, status
from app.core.models import User
from app.core.security.dependencies import get_current_user


async def get_current_seller(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is a seller."""
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can perform this action",
        )
    return current_user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user