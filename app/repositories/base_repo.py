from typing import TypeVar, Generic, Type, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository that provides standard CRUD Operations.
    Can be extended for any SQLAlchemy model.
    """

    model: Type[ModelType]

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_all(self, session: AsyncSession, limit: int = 100, offset: int = 0) -> Sequence[ModelType]:
        """Get a list of records (optionally paginated)"""

        result = await session.execute(select(self.model).offset(offset).limit(limit))
        return result.scalars().all()

    async def get_by_id(self, session: AsyncSession, obj_id: int) -> Optional[ModelType]:
        """Get a record by its ID."""
        return await session.get(self.model, obj_id)

    async def create(self, session: AsyncSession, **kwargs) -> ModelType:
        """Create a new record."""
        obj = self.model(**kwargs)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def update(self, session: AsyncSession, obj_id: int, data: dict) -> Optional[ModelType]:
        """Update an existing record by ID"""
        obj = await session.get(self.model, obj_id)
        if not obj:
            return None
        for field, value in data.items():
            setattr(obj, field, value)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, obj_id: int) -> Optional[ModelType]:
        """Delete a record by ID and return the deleted object."""
        obj = await session.get(self.model, obj_id)
        if not obj:
            return None
        await session.delete(obj)
        await session.commit()
        return obj
