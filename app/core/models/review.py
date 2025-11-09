from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
from .base import Base
from .mixins import IntIdPkMixin, CreatedAtMixin

if TYPE_CHECKING:
    from .product import Product
    from .user import User


class Review(Base, IntIdPkMixin, CreatedAtMixin):
    """
        Represents a user's review for a specific product.

        Each review includes a numeric rating (grade), an optional comment, and
        a timestamp of creation. Reviews are linked to both a user and a product.
        A user can only submit one review per product, enforced by a unique constraint.

        Relationships:
            user    — the User who wrote the review.
            product — the Product that was reviewed.

        Fields:
            user_id    — references the user who created the review.
            product_id — references the product being reviewed.
            comment    — optional textual comment provided by the user.
            grade      — numeric rating (typically 1–5 scale).
            is_active  — indicates whether the review is visible to users.

        Constraints:
            - Each (user_id, product_id) pair must be unique (one review per user per product).
            - Inherits CreatedAtMixin to automatically set creation timestamps.
        """
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_user_product_review"),)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship('User', back_populates='reviews')
    product: Mapped["Product"] = relationship('Product', back_populates='reviews')
