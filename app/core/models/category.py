from sqlalchemy import String, Boolean, Integer, Float, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING, Optional
from .base import Base
from .mixins import IntIdPkMixin

if TYPE_CHECKING:
    from .product import Product


class Category(Base, IntIdPkMixin):
    """
    Represents a product category within the system.
    A category can have a hierarchical structure:
    each category may have a parent and multiple child categories.
    Categories can also be marked as active or inactive.
    """
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[list["Product"]] = relationship("Product", back_populates='category', cascade='all, delete-orphan')
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id'), nullable=True)
    parent: Mapped[Optional["Category"]] = relationship('Category', back_populates='children',
                                                        remote_side='Category.id')
    children: Mapped[list["Category"]] = relationship("Category", back_populates='parent')
