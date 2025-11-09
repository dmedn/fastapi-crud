from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from .product import Product


class OrderItem(BaseModel):
    """
    Schema representing a single item within an order.
    Used in GET requests when retrieving order details.
    Each item includes product information, quantity, pricing, and total amount.
    """

    id: int = Field(..., description="Unique identifier of the order item.")
    product_id: int = Field(..., description="ID of the purchased product.")
    quantity: int = Field(..., ge=1, description="Quantity of the product purchased.")
    unit_price: Decimal = Field(..., ge=0, description="Unit price of the product at the time of purchase.")
    total_price: Decimal = Field(..., ge=0, description="Total price for this order item (quantity × unit price).")
    product: Optional[Product] = Field(None, description="Detailed information about the product (optional).")

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    """
    Schema representing a customer's order.
    Used in GET requests to return order information, including user ID,
    order status, total amount, and timestamps. Also includes the list of order items.
    """

    id: int = Field(..., description="Unique identifier of the order.")
    user_id: int = Field(..., description="ID of the user who placed the order.")
    status: str = Field(..., description="Current status of the order (e.g., pending, paid, shipped, delivered, canceled).")
    total_amount: Decimal = Field(..., ge=0, description="Total cost of the order, including all items.")
    created_at: datetime = Field(..., description="Date and time when the order was created.")
    updated_at: datetime = Field(..., description="Date and time when the order was last updated.")
    items: List[OrderItem] = Field(default_factory=list, description="List of order items included in this order.")

    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    """
    Schema for returning a paginated list of orders.
    Used in GET requests to retrieve multiple orders with pagination metadata.
    """

    items: List[Order] = Field(..., description="List of orders for the current page.")
    total: int = Field(ge=0, description="Total number of orders in the system.")
    page: int = Field(ge=1, description="Current page number (starting from 1).")
    page_size: int = Field(ge=1, description="Number of orders displayed per page.")

    model_config = ConfigDict(from_attributes=True)

