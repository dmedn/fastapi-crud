from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserCreate(BaseModel):
    """
    Schema for creating a new user account.

    Used for registration or account creation requests.
    Includes basic credentials and an optional role specification.
    """

    email: EmailStr = Field(
        description="The user's unique email address. Must be a valid email format."
    )
    password: str = Field(
        min_length=8,
        description="The user's password. Must contain at least 8 characters."
    )
    role: str = Field(
        default="buyer",
        pattern="^(buyer|seller|admin)$",
        description="The role of the user. Must be one of: 'buyer', 'seller', or 'admin'."
    )


class User(BaseModel):
    """
    Represents a user entity used in API responses.

    Returned when retrieving user information from the database.
    """

    id: int = Field(description="Unique identifier of the user.")
    email: EmailStr = Field(description="Email address of the user.")
    is_active: bool = Field(description="Indicates whether the user account is active.")
    role: str = Field(description="The user's assigned role: 'buyer', 'seller', or 'admin'.")

    model_config = ConfigDict(from_attributes=True)
