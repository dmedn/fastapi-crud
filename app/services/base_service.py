from typing import Generic, TypeVar, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from watchfiles import awatch

from app.repositories import BaseRepository

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """
    Generic base service that provides standard operations
    built on top of the repository layer
    """

    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    async def get_all(self, session: AsyncSession, limit: int = 100, offset: int = 0) -> Sequence[ModelType]:
        """Fetch multiple objects (with optional pagination)."""
        return await self.repository.get_all(session, limit, offset)

    async def get_by_id(self, session: AsyncSession, obj_id: int) -> Optional[ModelType]:
        """Fetch an object by its ID."""
        return await self.repository.get_by_id(session, obj_id)

    async def create(self, session: AsyncSession, **kwargs) -> ModelType:
        """Create a new object."""
        return await self.repository.create(session, **kwargs)

    async def update(self, session: AsyncSession, obj_id: int, data: dict) -> Optional[ModelType]:
        """Update an existing object."""
        return await self.repository.update(session, obj_id, data)

    async def delete(self, session: AsyncSession, obj_id: int) -> ModelType:
        """Delete an object by ID."""
        return await self.repository.delete(session, obj_id)
