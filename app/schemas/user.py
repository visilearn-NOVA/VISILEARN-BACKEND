"""
Pydantic schemas for User registration, profile updates, and authentication tokens.
"""

from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.models.user import UserRole


class UserBase(BaseModel):
    """
    Common user properties shared across create, read, and update schemas.
    """
    email: EmailStr = Field(..., description="Valid institutional or personal email address")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name of the user")


class UserCreate(UserBase):
    """
    Schema for new user registration with strict password policies.
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plaintext password (min 8 chars, at least 1 number or special char)"
    )
    role: Optional[UserRole] = Field(
        default=UserRole.STUDENT,
        description="Assigned system role (admin registration requires admin credentials)"
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(char.isdigit() for char in v) and not any(not char.isalnum() for char in v):
            raise ValueError("Password must contain at least one digit or special character.")
        return v


class UserUpdate(BaseModel):
    """
    Schema for updating user profile fields.
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """
    Safe public user representation without sensitive password hashes.
    """
    id: uuid.UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """
    Standard JSON login payload.
    """
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """
    JWT authentication payload returned upon successful login or refresh.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """
    Payload for acquiring a fresh access token using a refresh token.
    """
    refresh_token: str
