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
    Each user can leave only one review per product.
    Reviews include a numeric grade (rating), an optional comment,
    and a timestamp indicating when the review was created.
    """
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_user_product_review"))

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship('User', back_populates='reviews')
    product: Mapped["Product"] = relationship('Product', back_populates='reviews')
