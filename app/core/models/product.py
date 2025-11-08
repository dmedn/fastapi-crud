from sqlalchemy import String, Boolean, Integer, Float, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
from .base import Base
from .mixins import IntIdPkMixin

if TYPE_CHECKING:
    from .category import Category
    from .review import Review


class Product(Base, IntIdPkMixin):
    """
    Represents a product available for purchase.
    Each product belongs to a specific category and seller.
    It contains details such as name, description, price, stock quantity,
    and an aggregated rating calculated from reviews.
    """

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship(back_populates="products")
    seller_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    seller = relationship("User", back_populates='products')
    reviews: Mapped[list["Review"]] = relationship('Review', back_populates='product', cascade='all, delete-orphan')
