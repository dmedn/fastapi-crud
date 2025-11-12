from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional, Sequence

from app.repositories.user import UserRepository
from app.core.models import User
from app.services.base_service import BaseService


class UserService(BaseService[User]):
    """
    Service layer for managing users.
    Handles business logic such as registration,
    deactivation, and profile updates.
    """

    def __init__(self):
        self.repository: UserRepository = UserRepository()
        super().__init__(self.repository)

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """
        Retrieve user by email.
        """
        return await self.repository.get_by_email(session, email)

    async def create_user(
            self,
            session: AsyncSession,
            email: str,
            password: str,
            full_name: Optional[str] = None,
    ) -> User:
        """
        Create a new user record.
        """
        return await self.repository.create(
            session,
            email=email,
            password=password,
            full_name=full_name,
            is_active=True,
            role="customer",
        )

    async def get_active_users(self, session: AsyncSession) -> Sequence[User]:
        """
        Retrieve all active users.
        """
        return await self.repository.get_active_users(session)

    async def update_user(
            self, session: AsyncSession, user_id: int, data
    ) -> Optional[User]:
        """
        Update user profile.
        """
        update_data = data.dict(exclude_unset=True)
        return await self.repository.update(session, user_id, update_data)

    async def deactivate_user(self, session: AsyncSession, user_id: int) -> None:
        """
        Deactivate user (soft delete).
        """
        user = await self.repository.get_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.is_active = False
        await session.commit()
