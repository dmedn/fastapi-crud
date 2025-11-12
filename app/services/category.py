from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.models import Category
from app.repositories import CategoryRepository
from app.services import BaseService


class CategoryService(BaseService[Category]):
    """
    Service layer for managing product categories.
    Provides higher-level business operations on top of
    CategoryRepository, including validation, hierarchical
    operations, and safe activation/deactivation logic.
    """

    def __init__(self):
        """Initialize service with CategoryRepository."""
        self.repository: CategoryRepository = CategoryRepository()
        super().__init__(self.repository)

    async def get_active_categories(self, session: AsyncSession) -> Sequence[Category]:
        """
        Retrieve all active categories.
        Args:
            session (AsyncSession): SQLAlchemy async session.
        Returns:
            Sequence[Category]: List of active categories.
        """
        return await self.repository.get_active_categories(session)

    async def get_subcategories(self, session: AsyncSession, parent_id: int) -> Sequence[Category]:
        """
        Retrieve all subcategories of a given parent category.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            parent_id (int): ID of the parent category.
        Returns:
            Sequence[Category]: List of subcategories.
        """
        return await self.repository.get_subcategories(session, parent_id)

    async def get_root_categories(self, session: AsyncSession) -> Sequence[Category]:
        """
        Retrieve all root (top-level) categories.
        Args:
            session (AsyncSession): SQLAlchemy async session.
        Returns:
            Sequence[Category]: List of root categories.
        """
        return await self.repository.get_root_categories(session)

    async def get_category_hierarchy(self, session: AsyncSession, category_id: int) -> dict:
        """
        Retrieve the full hierarchy (parent → children) for a given category.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            category_id (int): ID of the category to explore.
        Returns:
            dict: A dictionary representation of the category tree.
        """

        category = await self.repository.get_by_id(session, category_id)

        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')

        async def _build_tree(cat: Category):
            children = await self.repository.get_subcategories(session, cat.id)
            return {
                "id": cat.id,
                "name": cat.name,
                "is_active": cat.is_active,
                "children": [await _build_tree(child) for child in children]
            }

        return await _build_tree(category)

    async def deactivate_category(self, session: AsyncSession, category_id) -> None:
        """
        Deactivate a category and all its subcategories recursively.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            category_id (int): ID of the category to deactivate.
        Raises:
            HTTPException: If category not found.
        """
        category = await self.repository.get_by_id(session, category_id)

        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        async def _deactivate_recursively(cat: Category):
            cat.is_active = False
            subcategories = await self.repository.get_subcategories(session, cat.id)
            for sub in subcategories:
                await _deactivate_recursively(sub)

        await _deactivate_recursively(category)
        await session.commit()

    async def activate_category(self, session: AsyncSession, category_id: int) -> Category:
        """
        Activate a category (and optionally its parent chain if needed).
        Args:
            session (AsyncSession): SQLAlchemy async session.
            category_id (int): ID of the category to activate.
        Returns:
            Category: Updated active category.
        Raises:
            HTTPException: If category not found.
        """

        category = await self.repository.get_by_id(session, category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catgory not found")
        parent = category.parent
        while parent:
            parent.is_active = True
            parent = parent.parent
        category.is_active = True
        await session.commit()
        await session.refresh(category)
        return category
