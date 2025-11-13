from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Sequence
from app.core.models import CartItem, User
from app.repositories import CartRepository, ProductRepository
from app.services import BaseService


class CartService(BaseService[CartItem]):
    """
    Service layer for managing user's shopping cart.
    Provides operations for adding, updating, and removing cart items,
    as well as calculating total quantity and price.
    """

    def __init__(self):
        """Initialize CartService with CartRepository and ProductRepository."""
        self.repository: CartRepository = CartRepository()
        super().__init__(self.repository)
        self.product_repo = ProductRepository()

    async def add_to_cart(
        self,
        session: AsyncSession,
        user: User,
        product_id: int,
        quantity: int = 1,
    ) -> CartItem:
        """
        Add a product to user's cart or increase its quantity if it already exists.
        Args:
            session (AsyncSession): Database session.
            user (User): Authenticated user.
            product_id (int): ID of the product to add.
            quantity (int): Quantity to add.
        Returns:
            CartItem: The updated or newly created cart item.
        Raises:
            HTTPException: If product doesn't exist or is inactive, or not enough stock.
        """
        product = await self.product_repo.get_by_id(session, product_id)
        if not product or not product.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

        if product.stock < quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock")

        existing_item = await self.repository.get_item(session, user.id, product_id)

        if existing_item:
            new_quantity = existing_item.quantity + quantity
            if new_quantity > product.stock:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity exceeds stock limit")
            existing_item.quantity = new_quantity
            await session.commit()
            await session.refresh(existing_item)
            return existing_item

        return await self.repository.create(
            session,
            user_id=user.id,
            product_id=product_id,
            quantity=quantity,
        )

    async def update_quantity(
        self,
        session: AsyncSession,
        user: User,
        product_id: int,
        quantity: int,
    ) -> CartItem:
        """
        Update the quantity of a specific product in the user's cart.
        Args:
            session (AsyncSession): Database session.
            user (User): Authenticated user.
            product_id (int): ID of the product to update.
            quantity (int): New quantity.
        Returns:
            CartItem: Updated cart item.
        Raises:
            HTTPException: If product not found in cart or invalid quantity.
        """
        item = await self.repository.remove_item(session, user.id, product_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found in cart")

        if quantity <= 0:
            await self.repository.remove_item(session, user.id, product_id)
            return item

        product = await self.product_repo.get_by_id(session, product_id)
        if quantity > product.stock:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity exceeds stock limit")

        item.quantity = quantity
        await session.commit()
        await session.refresh(item)
        return item

    async def remove_from_cart(self, session: AsyncSession, user: User, product_id: int) -> None:
        """
        Remove a specific product from the user's cart.
        Args:
            session (AsyncSession): Database session.
            user (User): Authenticated user.
            product_id (int): ID of the product to remove.
        """
        deleted = await self.repository.remove_item(session, user.id, product_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")

    async def get_user_cart(self, session: AsyncSession, user: User) -> dict:
        """
        Retrieve the full cart contents with totals.
        Args:
            session (AsyncSession): Database session.
            user (User): Authenticated user.
        Returns:
            dict: Cart details with items, total quantity, and total price.
        """
        items = await self.repository.get_user_cart(session, user.id)
        total_quantity = sum(item.quantity for item in items)
        total_price = sum(item.quantity * item.product.price for item in items)

        return {
            "user_id": user.id,
            "items": items,
            "total_quantity": total_quantity,
            "total_price": total_price,
        }

    async def clear_cart(self, session: AsyncSession, user: User) -> None:
        """
        Remove all items from a user's cart.
        Args:
            session (AsyncSession): Database session.
            user (User): Authenticated user.

        Raises:
            HTTPException: If the cart is already empty.
        """
        cart_items: Sequence[CartItem] = await self.repository.filter_by(session, user_id=user.id)
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is already empty."
            )

        for item in cart_items:
            await session.delete(item)

        await session.commit()