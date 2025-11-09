from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Sequence
from app.core.models import Category
from app.repositories.base_repo import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """
    Repository for managing Category entities.
    Extends the BaseRepository to provide additional methods specific to
    category management, including operations for working with hierarchical
    category structures and filtering active categories.
    """

    def __init__(self):
        super().__init__(Category)


    async def get_active_categories(self, session: AsyncSession) -> Sequence[Category]:
        """
        Retrieve all categories that are marked as active.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
        Returns:
            Sequence[Category]: A list of active Category objects.
        """
        result = await session.execute(select(self.model).where(self.model.is_active == True))
        return result.scalars().all()

    async def get_subcategories(self, session: AsyncSession, parent_id: int) -> Sequence[Category]:
        """
        Retrieve all subcategories belonging to a specific parent category.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            parent_id (int): ID of the parent category.
        Returns:
            Sequence[Category]: A list of subcategories.
        """
        result = await session.execute(select(self.model).where(self.model.parent_id == parent_id))
        return result.scalars().all()

    async def get_parent_category(self, session: AsyncSession, category_id: int) -> Optional[Category]:
        """
        Retrieve the parent category of a given category, if it exists.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            category_id (int): ID of the category whose parent should be retrieved.
        Returns:
            Optional[Category]: The parent Category object or None if not found.
        """

        stmt = (
            select(self.model)
            .join(self.model, self.model.id == self.model.parent_id, isouter=True)
            .where(self.model.id == category_id)
        )

        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_root_categories(self, session: AsyncSession) -> Sequence[Category]:
        """
        Retrieve all top-level categories (those without a parent).
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
        Returns:
            Sequence[Category]: A list of top-level categories.
        """
        result = await session.execute(select(self.model).where(self.model.parent_id.is_(None)))
        return result.scalars().all()
