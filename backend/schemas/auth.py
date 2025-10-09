# ==== backend/schemas/auth.py ====
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    """Enum for user roles."""
    ADMIN = "admin"
    AGENT = "agent"
    ENDUSER = "enduser"

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    # Role is set by default or by admin endpoints, not by direct registration

class UserLogin(BaseModel):
    """Schema for user login (used internally by OAuth2PasswordRequestForm)."""
    username: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schema for user data returned in API responses."""
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True # For SQLAlchemy compatibility

class UserPayload(BaseModel):
    """Schema for the payload extracted from a JWT token."""
    email: EmailStr
    role: UserRole

class Token(BaseModel):
    """Schema for the JWT token response."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for data contained within a JWT token."""
    email: Optional[EmailStr] = None
    role: Optional[str] = None # Store as string, convert to UserRole where needed