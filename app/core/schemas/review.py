from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ReviewSchema(BaseModel):
    """
    Represents a review entity used in API responses.
    This schema defines how reviews are returned to the client,
    including information about the user, product, rating, and content.
    """

    id: int = Field(description="Unique identifier of the review.")
    user_id: int = Field(description="Identifier of the user who wrote the review.")
    product_id: int = Field(description="Identifier of the reviewed product.")
    comment: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional textual content of the review (up to 500 characters)."
    )
    grade: int = Field(ge=1, le=5, description="The numeric rating given by the user (1–5).")
    created_at: datetime = Field(description="The UTC timestamp when the review was created.")
    is_active: bool = Field(description="Indicates whether the review is currently active.")

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    """
    Schema for creating a new review.
    Defines the required fields for submitting a product review.
    Each user can leave only one review per product.
    """

    product_id: int = Field(description="Identifier of the product being reviewed.")
    comment: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional comment text for the review (up to 500 characters)."
    )
    grade: int = Field(
        ge=1,
        le=5,
        description="Numeric rating of the product from 1 (poor) to 5 (excellent)."
    )
