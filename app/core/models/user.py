from sqlalchemy import String, Boolean, Integer, Float, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
from .base import Base
from .mixins import IntIdPkMixin

if TYPE_CHECKING:
    from .product import Product
    from .review import Review
    from .order import Order
    from .cart import CartItem

class User(Base, IntIdPkMixin):
    """
    Represents a user account within the system.

    Each user has a unique email and a securely hashed password used for authentication.
    Users can have different roles — such as 'buyer', 'seller', or 'admin' — which define
    their permissions and available actions in the system.

    A user can create products (if they are a seller), write reviews for products,
    and place orders. Deleting a user will automatically remove all their associated
    products, reviews, and orders to maintain referential integrity.

    Relationships:
        products — list of Product entities created by the user (for sellers).
        reviews  — list of Review entities written by the user.
        orders   — list of Order entities placed by the user.

    Fields:
        email          — unique email address used as the login identifier.
        hashed_password — securely stored hashed password (never exposed via API).
        is_active      — indicates whether the user account is active.
        role           — defines user privileges ('buyer', 'seller', or 'admin').

    Notes:
        - The `email` field is unique and indexed for fast lookups.
        - Role-based logic is enforced in business logic and authorization layers.
        - Cascade deletion is enabled for related orders and products.
    """

    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String, default='buyer')
    products: Mapped[list["Product"]] = relationship('Product', back_populates='seller')
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates='user', )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates='user', cascade="all, delete-orphan")
    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates='user', cascade="all, delete-orphan")