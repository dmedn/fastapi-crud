from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from .base import Base
from .mixins import IntIdPkMixin, CreatedAtMixin

if TYPE_CHECKING:
    from .product import Product
    from .user import User

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from .base import Base
from .mixins import IntIdPkMixin, CreatedAtMixin

if TYPE_CHECKING:
    from .product import Product
    from .user import User


class CartItem(Base, IntIdPkMixin, CreatedAtMixin):
    """
    Represents an individual item within a user's shopping cart.

    Each CartItem corresponds to a specific product added by a user,
    along with the desired quantity. The combination of `user_id` and
    `product_id` is unique, ensuring that a product can appear only once
    in a user's cart. If the same product is added multiple times, its
    quantity is incremented instead of creating a duplicate record.

    Attributes:
        user_id (int): The ID of the user who owns the cart.
        product_id (int): The ID of the product added to the cart.
        quantity (int): The number of units of the product in the cart.
        updated_at (datetime): Timestamp of the last modification.
            Automatically updated whenever the record changes.

    Relationships:
        user (User): The user who owns the cart item.
        product (Product): The product associated with this cart item.

    Notes:
        - Each user can have exactly one cart, composed of multiple CartItem records.
        - If a user or product is deleted, related cart items are automatically removed.
    """

    __tablename__ = "cart_items"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="cart_items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_items_user_product"),
    )
