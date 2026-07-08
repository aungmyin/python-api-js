from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List

# Category schemas
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

# Product schemas
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category_id: Optional[int] = Field(None, gt=0)

    @validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

    @validator('price')
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return round(v, 2)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = Field(None, gt=0)

    @validator('price')
    def price_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return round(v, 2) if v is not None else None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    category_id: Optional[int]
    category: Optional[CategoryResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# User schemas
class UserCreate(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    full_name: str = Field(..., min_length=2, max_length=255)

    @validator('email')
    def email_valid(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v.lower()

    @validator('password')
    def password_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True

# Auth schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)
