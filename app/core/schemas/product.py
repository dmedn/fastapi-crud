from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class Product(BaseModel):
    """
    Represents a product entity used in API responses.
    This model defines the structure of a product returned by the API.
    It includes basic information such as name, description, price, stock quantity,
    category association, and activity status.
    """
    id: int = Field(description="Unique identifier of the product.")
    name: str = Field(description="The name of the product.")
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="A short description of the product (up to 500 characters).",
    )
    price: float = Field(gt=0, description="The price of the product. Must be greater than 0.")
    stock: int = Field(ge=0, description="The quantity of this product available in stock (>= 0).")
    category_id: int = Field(description="Identifier of the category this product belongs to.")
    is_active: bool = Field(description="Indicates whether the product is active and available for sale.")
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Schema for creating a new product.
    This model defines the data required to create a new product.
    All fields are mandatory except for the optional description.
    """

    name: str = Field(
        min_length=3,
        max_length=100,
        description="The name of the product. Must be between 3 and 100 characters long."
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="An optional description of the product (up to 500 characters)."
    )
    price: float = Field(
        gt=0,
        description="The price of the product. Must be greater than 0."
    )
    stock: int = Field(
        ge=0,
        description="The available quantity of the product (must be non-negative)."
    )
    category_id: int = Field(
        description="The ID of the category this product belongs to."
    )
    is_active: bool = Field(
        default=True,
        description="Indicates whether the product is active upon creation."
    )


class ProductUpdate(BaseModel):
    """
    Schema for updating an existing product.
    All fields are optional — only the provided ones will be updated.
    Useful for partial updates via PATCH requests.
    """

    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="The updated name of the product (optional)."
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="An updated description of the product (optional)."
    )
    price: Optional[float] = Field(
        None,
        gt=0,
        description="The updated price of the product (must be greater than 0)."
    )
    stock: Optional[int] = Field(
        None,
        ge=0,
        description="The updated stock quantity (must be non-negative)."
    )
    category_id: Optional[int] = Field(
        None,
        description="The updated category ID (optional)."
    )
    is_active: Optional[bool] = Field(
        None,
        description="Indicates whether the product remains active (optional)."
    )
