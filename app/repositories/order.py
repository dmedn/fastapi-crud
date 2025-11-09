from typing import Sequence, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.models import Order, OrderItem
from app.repositories.base_repo import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """
    Repository for managing Order entities and their related OrderItem records.
    Provides CRUD operations (inherited from BaseRepository) and additional
    query methods for filtering, status updates, and fetching orders with items.
    """

    def __init__(self):
        """Initialize the repository with the Order model."""
        super().__init__(Order)

    async def get_by_user(self, session: AsyncSession, user_id: int) -> Sequence[Order]:
        """
        Retrieve all orders belonging to a specific user.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            user_id (int): ID of the user.
        Returns:
            Sequence[Order]: List of orders placed by the user.
        """
        result = await session.execute(
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(selectinload(self.model.items))
        )
        return result.scalars().all()

    async def get_with_items(self, session: AsyncSession, order_id: int) -> Optional[Order]:
        """
        Retrieve a single order along with all its related order items.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            order_id (int): ID of the order to retrieve.
        Returns:
            Optional[Order]: The order with items, or None if not found.
        """
        result = await session.execute(
            select(self.model)
            .where(self.model.id == order_id)
            .options(selectinload(self.model.items))
        )
        return result.scalars().first()

    async def get_by_status(self, session: AsyncSession, status: str) -> Sequence[Order]:
        """
        Retrieve all orders filtered by a specific status.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            status (str): Order status to filter by (e.g., 'pending', 'completed').
        Returns:
            Sequence[Order]: List of orders matching the given status.
        """
        result = await session.execute(
            select(self.model).where(self.model.status == status)
        )
        return result.scalars().all()

    async def update_status(self, session: AsyncSession, order_id: int, status: str) -> Optional[Order]:
        """
        Update the status of an existing order and return the updated record.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            order_id (int): ID of the order to update.
            status (str): New status value.
        Returns:
            Optional[Order]: The updated Order object or None if not found.
        """
        result = await session.execute(
            update(self.model)
            .where(self.model.id == order_id)
            .values(status=status)
            .returning(self.model)
        )
        await session.commit()
        return result.scalars().first()

    async def get_seller_orders(self, session: AsyncSession, seller_id: int) -> Sequence[Order]:
        """
        Retrieve all orders that include at least one product from a specific seller.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            seller_id (int): ID of the seller whose sales should be retrieved.
        Returns:
            Sequence[Order]: List of orders containing the seller's products.
        """
        result = await session.execute(
            select(self.model)
            .join(OrderItem)
            .join(OrderItem.product)
            .where(OrderItem.product.has(seller_id=seller_id))
            .options(selectinload(self.model.items))
            .distinct()
        )
        return result.scalars().all()
