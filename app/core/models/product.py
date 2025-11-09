from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Computed, Index
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from typing import TYPE_CHECKING
from .base import Base
from .mixins import IntIdPkMixin

if TYPE_CHECKING:
    from .category import Category
    from .review import Review
    from .order import OrderItem


class Product(Base, IntIdPkMixin):
    """
    Represents a product available for purchase.

    Each product belongs to a specific category and seller, and can have multiple
    reviews and order items associated with it. The product model contains essential
    details such as name, description, price, stock quantity, and an aggregated rating
    calculated from user reviews.

    Additionally, the model supports full-text search through a PostgreSQL TSVECTOR
    field that indexes product names and descriptions for efficient keyword lookups.

    Relationships:
        category    — the Category this product belongs to.
        seller      — the User who sells the product.
        reviews     — a list of Review entities related to this product.
        order_items — the OrderItem records where this product was purchased.

    Fields:
        name         — the product name (up to 100 characters).
        description  — an optional text description (up to 500 characters).
        price        — the price of the product (must be > 0).
        stock        — available quantity of the product in inventory.
        is_active    — indicates if the product is currently available for purchase.
        rating       — the average rating based on user reviews.
        tsv          — a computed TSVECTOR field used for full-text search.

    Notes:
        - A GIN index is created on the TSVECTOR column for optimized search queries.
        - The TSVECTOR combines weighted text from both name ('A') and description ('B').
        - Reviews and order items are automatically deleted when the product is removed.
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
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates='product')
    tsv: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed(
            """
            setweight(to_tsvector('english', coalesce(name, '')), 'A')
            || 
            setweight(to_tsvector('english', coalesce(description, '')), 'B')
            """,
            persisted=True
        ),
        nullable=False
    )

    __table_args__ = (
        Index('ix_products_tsv_gin', "tsv", postgresql_using='gin')
    )
