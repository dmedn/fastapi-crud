from sqlalchemy import String, Integer, Boolean, Numeric, func, ForeignKey, DateTime
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from .base import Base
from .mixins import IntIdPkMixin, CreatedAtMixin

if TYPE_CHECKING:
    from .user import User
    from .product import Product


class OrderItem(Base, IntIdPkMixin):
    """
        Represents a single item within an order.
        This model stores information about a purchased product, including
        the quantity, unit price at the time of purchase, and the total price
        for the item. It connects orders and products, and is removed
        automatically when the related order is deleted.
        Relationships:
            order  — the parent Order entity.
            product — the associated Product entity.
        Notes:
            - `unit_price` and `total_price` are stored as fixed-point decimals
              (Numeric) to ensure precise monetary calculations.
            - `ondelete="CASCADE"` ensures that order items are deleted
              automatically when their parent order is removed.
        """
    __tablename__ = "order_items"
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates='items')
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")


class Order(Base, IntIdPkMixin, CreatedAtMixin):
    """
        Represents a customer order.
        This model contains information about the user who placed the order,
        its current processing status, the total amount, and timestamps for
        creation and updates. Each order consists of one or more OrderItem
        entries representing individual purchased products.
        Relationships:
            user  — the User who created the order.
            items — the list of OrderItem entries associated with this order.
        Fields:
            user_id      — identifies the user who placed the order.
            status       — order status (e.g., pending, paid, shipped, delivered, canceled).
            total_amount — aggregated monetary value of all order items.
            updated_at   — timestamp automatically updated on modification.
        Notes:
            - Uses `CreatedAtMixin` for automatic creation timestamp.
            - `updated_at` is maintained using a server-side `NOW()` function.
            - Setting `cascade="all, delete-orphan"` ensures all order items
              are removed if the order itself is deleted.
        """
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default='pending', nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
