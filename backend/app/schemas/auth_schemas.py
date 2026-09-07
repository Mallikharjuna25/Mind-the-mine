"""
Authentication & User Pydantic Schemas
"""

import re
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email address format")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    full_name: str
    mine_id: Optional[str] = None
    permissions: List[str] = []


class UserCreate(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)
    full_name: str
    role: str
    designation: Optional[str] = None
    phone_number: Optional[str] = None
    mine_id: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email address format")
        return v


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    designation: Optional[str] = None
    phone_number: Optional[str] = None
    mine_id: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
