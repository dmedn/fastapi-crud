from typing import Generic, TypeVar, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import BaseRepository

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """
    Generic base service that provides standard CRUD operations
    built on top of the repository layer.
    This class serves as a foundation for domain-specific services,
    combining business logic and database interactions through repositories.
    """

    def __init__(self, repository: BaseRepository[ModelType]):
        """
        Initialize the service with a repository instance.
        Args:
            repository (BaseRepository): The repository responsible
                                         for data persistence and retrieval.
        """
        self.repository = repository

    async def get_all(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ) -> Sequence[ModelType]:
        """
        Retrieve multiple objects (optionally paginated).
        Args:
            session (AsyncSession): SQLAlchemy async session.
            limit (int): Maximum number of records to return.
            offset (int): Number of records to skip.
        Returns:
            Sequence[ModelType]: List of database objects.
        """
        return await self.repository.get_all(session, limit, offset)

    async def get_by_id(
        self,
        session: AsyncSession,
        obj_id: int
    ) -> Optional[ModelType]:
        """
        Retrieve a single object by its ID.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_id (int): Object identifier.
        Returns:
            Optional[ModelType]: The found object or None.
        """
        return await self.repository.get_by_id(session, obj_id)

    async def create(
        self,
        session: AsyncSession,
        **kwargs
    ) -> ModelType:
        """
        Create a new database object.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            **kwargs: Fields required for object creation.
        Returns:
            ModelType: The newly created object.
        """
        return await self.repository.create(session, **kwargs)

    async def update(
        self,
        session: AsyncSession,
        obj_id: int,
        data: dict
    ) -> Optional[ModelType]:
        """
        Update an existing object by ID.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_id (int): Object identifier.
            data (dict): Fields to update.
        Returns:
            Optional[ModelType]: Updated object or None if not found.
        """
        return await self.repository.update(session, obj_id, data)

    async def delete(
        self,
        session: AsyncSession,
        obj_id: int
    ) -> Optional[ModelType]:
        """
        Delete an object by ID.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            obj_id (int): Object identifier.
        Returns:
            Optional[ModelType]: The deleted object or None if not found.
        """
        return await self.repository.delete(session, obj_id)