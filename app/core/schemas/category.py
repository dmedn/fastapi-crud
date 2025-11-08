from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional


class CategoryCreate(BaseModel):
    """
    Schema for creating a new category.
    Used in POST requests when adding a new category.
    Contains the required and optional fields for creating
    a record in the database.
    """
    name: str = Field(min_length=3, max_length=50,
                      description="The name of the category. Must be between 3 and 50 characters long.")
    parent_id: Optional[int] = Field(None,
                                     description="The ID of the parent category, if this category is a subcategory. "
                                                 "If it's a top-level category, this field can be omitted.")


class CategoryUpdate(BaseModel):
    """
    Schema for updating an existing category.
    Used in PATCH or PUT requests when modifying a category.
    All fields are optional — you can update one or several attributes.
    """
    id: Optional[int] = Field(None, min_length=3, max_length=50,
                              description="The new name of the category. Must be between 3 and 50 characters long.")
    parent_id: Optional[int] = Field(None,
                                     description='The new parent category ID, if this category should become a subcategory. If set to null, the category will become a top-level category')


class Category(BaseModel):
    """
    Schema for representing a category in API responses.
    Used in GET requests to return category data.
    Typically corresponds to a database record.
    """
    id: int = Field(description="Unique identifier of the category.")
    name: str = Field(min_length=3, max_length=50,
                      description="The name of the category. Must be between 3 and 50 characters long."
                      )
    parent_id: Optional[int] = Field(None, description="ID of the parent category, if this category is a subcategory. "
                                                       "If null, the category is a top-level category."
                                     )
    is_active: bool = Field(description="Indicates whether the category is active and visible to users.")
    model_config = ConfigDict(from_attributes=True)


class CategoryList(BaseModel):
    """
    Schema for returning a paginated list of categories.
    Used in GET requests that return multiple categories, typically with pagination.
    Contains metadata such as the total number of records and the current page.
    """

    total: int = Field(description='Total number of categories available in the database.')
    page: int = Field(description='The current page number (starting from 1).')
    limit: int = Field(description='The maximum number of categories returned per page.')
    items: list[Category] = Field(description='A list of category objects for the current page.')