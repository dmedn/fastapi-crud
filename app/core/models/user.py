from sqlalchemy import String, Boolean, Integer, Float, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
from .base import Base
from .mixins import IntIdPkMixin

if TYPE_CHECKING:
    from .product import Product
    from .review import Review


class User(Base, IntIdPkMixin):
    """
    Represents a user account in the system.
    A user can have different roles (e.g., buyer, seller),
    create products for sale, and write reviews for products.
    Each user has a unique email and a hashed password for authentication.
    """
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String, default='buyer')
    products: Mapped[list["Product"]] = relationship('Product', back_populates='seller')
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates='user', )
