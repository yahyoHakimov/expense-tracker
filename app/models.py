from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

# Expense categories
class ExpenseCategory(str, enum.Enum):
    GROCERIES = "groceries"
    LEISURE = "leisure"
    ELECTRONICS = "electronics"
    UTILITIES = "utilities"
    CLOTHING = "clothing"
    HEALTH = "health"
    OTHERS = "others"

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship: 1 user → many expenses
    expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")

# Expense model
class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)  # 10 digits, 2 decimal places
    category = Column(Enum(ExpenseCategory), nullable=False)
    description = Column(String(500))
    date = Column(Date, nullable=False, index=True)  # Expense date
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship: expense → user
    owner = relationship("User", back_populates="expenses")