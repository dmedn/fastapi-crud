from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.core.models import User
from app.core.models.db_helper import db_helper
from app.core.schemas import Category, CategoryCreate, CategoryUpdate
from app.core.security.roles import get_current_admin
from app.services import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])
category_service = CategoryService()


@router.post(
    "/",
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    description="Create a new product category. Only admins can perform this action.",
)
async def create_category(
        category_data: CategoryCreate,
        session: AsyncSession = Depends(db_helper.get_async_db),
        current_user: User = Depends(get_current_admin),
):
    """Endpoint for creating a new category."""
    return await category_service.create(session, **category_data.model_dump())


@router.get(
    "/{category_id}",
    response_model=Category,
    summary="Get category by ID",
    description="Retrieve details for a single category by its ID.",
)
async def get_category_by_id(
        category_id: int,
        session: AsyncSession = Depends(db_helper.get_async_db),
):
    """Retrieve a specific category by ID."""
    category = await category_service.get_by_id(session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get(
    "/",
    response_model=Sequence[Category],
    summary="List all categories",
    description="Retrieve a list of all categories with optional pagination.",
)
async def list_categories(
        session: AsyncSession = Depends(db_helper.get_async_db),
        limit: int = 100,
        offset: int = 0,
):
    """Retrieve a paginated list of all categories."""
    return await category_service.get_all(session, limit, offset)


@router.get(
    "/active",
    response_model=Sequence[Category],
    summary="List active categories",
    description="Retrieve all categories that are currently active.",
)
async def get_active_categories(
        session: AsyncSession = Depends(db_helper.get_async_db),
):
    """Get all categories where is_active=True."""
    return await category_service.get_active_categories(session)


@router.get(
    "/{parent_id}/subcategories",
    response_model=Sequence[Category],
    summary="List subcategories of a category",
    description="Retrieve all subcategories that belong to a given parent category.",
)
async def get_subcategories(
        parent_id: int,
        session: AsyncSession = Depends(db_helper.get_async_db),
):
    """Retrieve subcategories by parent category ID."""
    return await category_service.get_subcategories(session, parent_id)


@router.get(
    "/{category_id}/hierarchy",
    summary="Get category hierarchy",
    description="Retrieve full category hierarchy (parent and all descendants) starting from a specific category.",
)
async def get_category_hierarchy(
        category_id: int,
        session: AsyncSession = Depends(db_helper.get_async_db),
):
    """Get full nested structure of a category and its children."""
    return await category_service.get_category_hierarchy(session, category_id)


@router.patch(
    "/{category_id}",
    response_model=Category,
    summary="Update category",
    description="Update category fields (e.g., name, description). Only admins can perform this action.",
)
async def update_category(
        category_id: int,
        category_data: CategoryUpdate,
        session: AsyncSession = Depends(db_helper.get_async_db),
        current_user: User = Depends(get_current_admin),
):
    """Update an existing category."""
    updated = await category_service.update(session, category_id, category_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated


@router.post(
    "/{category_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a category",
    description="Deactivate a category and all its subcategories recursively. Only admins can perform this action.",
)
async def deactivate_category(
        category_id: int,
        session: AsyncSession = Depends(db_helper.get_async_db),
        current_user: User = Depends(get_current_admin),
):
    """Deactivate a category by ID."""
    await category_service.deactivate_category(session, category_id)
    return None


@router.post(
    "/{category_id}/activate",
    response_model=Category,
    summary="Activate a category",
    description="Activate a category and its parent hierarchy. Only admins can perform this action.",
)
async def activate_category(
        category_id: int,
        session: AsyncSession = Depends(db_helper.get_async_db),
        current_user: User = Depends(get_current_admin),
):
    """Activate a category by ID."""
    return await category_service.activate_category(session, category_id)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category",
    description="Delete a category permanently. Only admins can perform this action.",
)
async def delete_category(
        category_id: int,
        session: AsyncSession = Depends(db_helper.get_async_db),
        current_user: User = Depends(get_current_admin),
):
    """Permanently delete a category."""
    category = await category_service.get_by_id(session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await category_service.delete(session, category_id)
    return None
