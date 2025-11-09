from typing import Optional, Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User, CartItem
from app.repositories.base_repo import BaseRepository
from app.core.security import verify_password


class UserRepository(BaseRepository[User]):
    """
    Repository for managing User entities.
    Extends the BaseRepository to include additional methods for
    working with user authentication, role management, and account activation.
    """
    def __init__(self):
        """Initialize the repository with the User model."""
        super().__init__(User)

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """
        Retrieve a user by email address.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            email (str): Email address of the user.
        Returns:
            Optional[User]: User object if found, otherwise None.
        """
        result = await session.execute(select(self.model).where(self.model.email == email))
        return result.scalars().first()

    async def get_by_role(self, session: AsyncSession, role: str) -> Sequence[User]:
        """
        Retrieve all active users with a specific role.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            role (str): Role of the users to retrieve (e.g., 'seller', 'admin', 'buyer').
        Returns:
            Sequence[User]: List of users with the given role.
        """
        result = await session.execute(
            select(self.model).where(
                self.model.role == role,
                self.model.is_active.is_(True)
            )
        )
        return result.scalars().all()

    async def verify_credentials(
        self, session: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """
        Verify user credentials by comparing a provided password with the stored hash.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            email (str): User's email.
            password (str): Plain-text password to verify.
        Returns:
            Optional[User]: Authenticated User object if credentials are valid, otherwise None.
        """
        user = await self.get_by_email(session, email)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def activate_user(self, session: AsyncSession, user_id: int) -> Optional[User]:
        """
        Activate a user account by setting `is_active = True`.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            user_id (int): ID of the user to activate.
        Returns:
            Optional[User]: Updated User object, or None if not found.
        """
        result = await session.execute(
            update(self.model)
            .where(self.model.id == user_id)
            .values(is_active=True)
            .returning(self.model)
        )
        await session.commit()
        return result.scalars().first()

    async def deactivate_user(self, session: AsyncSession, user_id: int) -> Optional[User]:
        """
        Deactivate a user account by setting `is_active = False`.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            user_id (int): ID of the user to deactivate.
        Returns:
            Optional[User]: Updated User object, or None if not found.
        """
        result = await session.execute(
            update(self.model)
            .where(self.model.id == user_id)
            .values(is_active=False)
            .returning(self.model)
        )
        await session.commit()
        return result.scalars().first()

    async def get_cart_items(self, session: AsyncSession, user_id: int) -> Sequence[CartItem]:
        """
        Retrieve all items in a user's shopping cart.

        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            user_id (int): ID of the user.

        Returns:
            Sequence[CartItem]: A list of CartItem objects belonging to the user.
        """
        result = await session.execute(select(CartItem).where(CartItem.user_id == user_id))
        return result.scalars().all()

    async def clear_cart(self, session: AsyncSession, user_id: int) -> None:
        """
        Remove all items from a user's shopping cart.

        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            user_id (int): ID of the user whose cart should be cleared.
        """
        await session.execute(delete(CartItem).where(CartItem.user_id == user_id))
        await session.commit()