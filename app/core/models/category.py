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

        Categories allow for hierarchical organization of products. Each category
        may have a parent category (for subcategories) and multiple child categories.
        The model also tracks whether a category is active, allowing temporary deactivation
        without deletion.

        Relationships:
            products — list of Product entities associated with this category.
            parent   — reference to the parent Category (if this is a subcategory).
            children — list of child Category entities (if any).

        Fields:
            name       — the category name.
            is_active  — indicates if the category is currently active.
            parent_id  — optional foreign key linking to the parent category.

        Notes:
            - Deleting a category will cascade and remove all related products.
            - The hierarchical structure is implemented using a self-referential relationship.
        """
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[list["Product"]] = relationship("Product", back_populates='category', cascade='all, delete-orphan')
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id'), nullable=True)
    parent: Mapped[Optional["Category"]] = relationship('Category', back_populates='children',
                                                        remote_side='Category.id')
    children: Mapped[list["Category"]] = relationship("Category", back_populates='parent')
