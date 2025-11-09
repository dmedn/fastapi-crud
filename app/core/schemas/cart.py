from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import List
from .product import Product


class CartItemBase(BaseModel):
    """
    Base schema for cart items.
    Defines the common fields shared between creation and update operations.
    """
    product_id: int = Field(..., description="The unique identifier of the product.")
    quantity: int = Field(..., ge=1, description="The number of units of the product in the cart.")


class CartItemCreate(CartItemBase):
    """
    Schema for adding a new product to the cart.
    Used in POST requests to create a new cart item.
    """
    pass


class CartItemUpdate(BaseModel):
    """
    Schema for updating the quantity of an existing cart item.
    Used in PATCH requests to modify the number of units.
    """
    quantity: int = Field(..., ge=1, description="The updated quantity of the product in the cart.")


class CartItem(BaseModel):
    """
    Schema for representing a single item in the user's cart.
    Includes product details and the selected quantity.
    """
    id: int = Field(..., description="Unique identifier of the cart item.")
    quantity: int = Field(..., ge=1, description="Number of product units added to the cart.")
    product: Product = Field(..., description="Detailed product information associated with this cart item.")

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    """
    Schema for representing the user's entire shopping cart.
    Contains all cart items, total quantity, and total price.
    """
    user_id: int = Field(..., description="Unique identifier of the user who owns the cart.")
    items: List[CartItem] = Field(default_factory=list, description="List of cart items belonging to the user.")
    total_quantity: int = Field(..., ge=0, description="Total number of products in the cart (sum of all item quantities).")
    total_price: Decimal = Field(..., ge=0, description="Total price of all products in the cart.")

    model_config = ConfigDict(from_attributes=True)
