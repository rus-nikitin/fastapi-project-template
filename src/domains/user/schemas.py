from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=100, description="User full name")


class UserCreate(UserBase):
    """Schema for creating a new user"""
    is_active: bool = Field(default=True, description="Whether the user is active")
    is_admin: bool = Field(default=False, description="Whether the user is an admin")


class UserUpdate(BaseModel):
    """Schema for updating an existing user"""
    email: Optional[EmailStr] = Field(None, description="User email address")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User full name")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")
    is_admin: Optional[bool] = Field(None, description="Whether the user is an admin")


class UserResponse(UserBase):
    """Schema for user response"""
    model_config = ConfigDict(
        from_attributes=True
    )
    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Whether the user is active")
    is_admin: bool = Field(..., description="Whether the user is an admin")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="User last update timestamp")
