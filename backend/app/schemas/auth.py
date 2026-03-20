"""Authentication schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterSchema(BaseModel):
    """User registration request."""

    email: EmailStr
    display_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)


class UserLoginSchema(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class UserSchema(BaseModel):
    """User info response."""

    id: str
    email: str
    display_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True
