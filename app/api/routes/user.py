from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User
from app.core.models import db_helper
from app.services import UserService
from app.core.security import create_access_token, create_refresh_token
from app.core.security import verify_password, hash_password
from app.core.security import get_current_user
from app.core.security import get_current_admin
from app.core.schemas import UserCreate, UserRead, TokenResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


user_service = UserService()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(db_helper.get_async_db),
):
    """
    Register a new user.
    Hashes the password and saves a new User record.
    """
    existing_user = await user_service.get_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    user = await user_service.create_user(
        session=session,
        email=user_data.email,
        password=hash_password(user_data.password),
        full_name=user_data.full_name,
    )
    return user


@router.post("/token", response_model=TokenResponse)
async def login_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(db_helper.get_async_db),
):
    """
    Authenticate user and return access/refresh JWT tokens.
    """
    user = await user_service.get_by_email(session, user_data.email)
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve currently authenticated user.
    """
    return current_user


@router.get("/active", response_model=list[UserRead])
async def get_active_users(
    session: AsyncSession = Depends(db_helper.get_async_db),
    _: User = Depends(get_current_admin),
):
    """
    Retrieve all active users (admin only).
    """
    users = await user_service.get_active_users(session)
    return users


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(db_helper.get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update user profile (self or admin).
    """
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot modify another user's account",
        )

    user = await user_service.update_user(session, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    session: AsyncSession = Depends(db_helper.get_async_db),
    _: User = Depends(get_current_admin),
):
    """
    Deactivate (soft delete) a user (admin only).
    """
    await user_service.deactivate_user(session, user_id)
    return None

