from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.models import Order, OrderItem, CartItem, Product, User
from app.repositories.order import OrderRepository
from app.repositories.cart import CartRepository
from app.repositories.product import ProductRepository
from app.services.base_service import BaseService


class OrderService(BaseService[Order]):
    """
    Service layer for managing orders.
    Handles creation of orders from user's cart,
    status updates, and order retrieval.
    """

    def __init__(self):
        self.repository = OrderRepository()
        super().__init__(self.repository)

        self.cart_repo = CartRepository()
        self.product_repo = ProductRepository()

    async def create_order_from_cart(
        self,
        session: AsyncSession,
        user: User,
    ) -> Order:
        """
        Create a new order using items from user's cart.
        Args:
            session (AsyncSession): DB session.
            user (User): Current authenticated user.
        Returns:
            Order: Created order.
        Raises:
            HTTPException: If cart is empty.
        """

        cart_items = await self.cart_repo.get_user_cart(session, user.id)

        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty.",
            )

        order = await self.repository.create(
            session,
            user_id=user.id,
            status="pending",
            total_amount=0,
        )

        total_amount = 0

        for item in cart_items:
            product = await self.product_repo.get_by_id(session, item.product_id)

            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {item.product_id} is unavailable.",
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for product {product.id}.",
                )

            product.stock -= item.quantity

            position_total = product.price * item.quantity
            total_amount += position_total

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
                total_price=position_total,
            )
            session.add(order_item)

        order.total_amount = total_amount

        await self.cart_repo.clear_cart(session, user.id)

        await session.commit()
        await session.refresh(order)
        return order

    async def get_user_orders(
        self, session: AsyncSession, user_id: int
    ) -> Sequence[Order]:
        """
        Return all orders belonging to a user.
        """
        return await self.repository.get_by_user(session, user_id)

    async def update_status(
        self,
        session: AsyncSession,
        order_id: int,
        new_status: str
    ) -> Order:
        """
        Update the status of an order (Admin only).
        """
        order = await self.repository.get_by_id(session, order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        order.status = new_status
        await session.commit()
        await session.refresh(order)
        return order
