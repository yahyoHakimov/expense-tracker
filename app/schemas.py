from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from app.models import ExpenseCategory

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class ExpenseBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    category: ExpenseCategory
    description: Optional[str] = Field(None, max_length=500)
    date: date
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[date] = None

class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class CategorySummary(BaseModel):
    category: ExpenseCategory
    total: Decimal
    count: int

class ExpenseSummary(BaseModel):
    total_amount: Decimal
    total_count: int
    categories: list[CategorySummary]