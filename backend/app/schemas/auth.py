"""Authentication and User Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: str
    full_name: str | None = None
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
