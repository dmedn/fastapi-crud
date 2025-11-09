from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.models import CartItem
from app.repositories import BaseRepository


class CartRepository(BaseRepository[CartItem]):
    """
    Repository for managing shopping cart items.
    A user's cart is represented as a collection of CartItem records.
    Each record corresponds to a specific product in the cart.
    The repository provides methods to add, update, remove, and clear
    items in the user's cart.
    """

    def __init__(self):
        """Initialize the repository with the CartItem model."""
        super().__init__(CartItem)

    async def add_to_cart(
        self,
        session: AsyncSession,
        user_id: int,
        product_id: int,
        quantity: int = 1,
    ) -> CartItem:
        """
        Add a product to the user's cart.
        If the product already exists, increment its quantity.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            user_id (int): ID of the user.
            product_id (int): ID of the product.
            quantity (int): Quantity to add (default: 1).
        Returns:
            CartItem: The created or updated CartItem object.
        """
        result = await session.execute(
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.product_id == product_id
            )
        )
        item = result.scalar_one_or_none()

        if item:
            item.quantity += quantity
            await session.commit()
            await session.refresh(item)
            return item

        new_item = self.model(user_id=user_id, product_id=product_id, quantity=quantity)
        session.add(new_item)
        await session.commit()
        await session.refresh(new_item)
        return new_item

    async def update_quantity(
        self,
        session: AsyncSession,
        cart_item_id: int,
        quantity: int,
    ) -> Optional[CartItem]:
        """
        Update the quantity of a specific cart item.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            cart_item_id (int): ID of the cart item.
            quantity (int): New quantity value.
        Returns:
            Optional[CartItem]: Updated CartItem or None if not found.
        """
        item = await session.get(self.model, cart_item_id)
        if not item:
            return None

        item.quantity = quantity
        await session.commit()
        await session.refresh(item)
        return item

    async def remove_item(
        self,
        session: AsyncSession,
        user_id: int,
        product_id: int,
    ) -> bool:
        """
        Remove a product from the user's cart.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            user_id (int): ID of the user.
            product_id (int): ID of the product to remove.
        Returns:
            bool: True if item was removed, False otherwise.
        """
        result = await session.execute(
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.product_id == product_id
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return False

        await session.delete(item)
        await session.commit()
        return True

    async def clear_cart(self, session: AsyncSession, user_id: int) -> None:
        """
        Clear all items in a user's cart.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            user_id (int): ID of the user whose cart should be cleared.
        """
        await session.execute(delete(self.model).where(self.model.user_id == user_id))
        await session.commit()

    async def get_user_cart(self, session: AsyncSession, user_id: int) -> Sequence[CartItem]:
        """
        Retrieve all cart items for a specific user.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            user_id (int): ID of the user.
        Returns:
            Sequence[CartItem]: A list of CartItem objects in the user's cart.
        """
        result = await session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().all()

