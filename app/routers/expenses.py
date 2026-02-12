from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, timedelta
from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)

# ========== CREATE EXPENSE ==========

@router.post("/", response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: schemas.ExpenseCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new expense
    
    Automatically assigns to current user
    """
    new_expense = models.Expense(
        **expense.model_dump(),
        user_id=current_user.id
    )
    
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return new_expense

# ========== GET ALL EXPENSES (with filters) ==========

@router.get("/", response_model=list[schemas.ExpenseResponse])
def get_expenses(
    period: Optional[str] = Query(None, description="week, month, 3months"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[models.ExpenseCategory] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all expenses for current user with optional filters
    
    Filters:
      - period: week, month, 3months
      - start_date & end_date: custom date range
      - category: filter by expense category
    """
    # Base query - only current user's expenses
    query = db.query(models.Expense).filter(
        models.Expense.user_id == current_user.id
    )
    
    # Date filtering
    if period:
        today = date.today()
        
        if period == "week":
            start = today - timedelta(days=7)
            query = query.filter(models.Expense.date >= start)
        
        elif period == "month":
            start = today - timedelta(days=30)
            query = query.filter(models.Expense.date >= start)
        
        elif period == "3months":
            start = today - timedelta(days=90)
            query = query.filter(models.Expense.date >= start)
    
    # Custom date range
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    
    if end_date:
        query = query.filter(models.Expense.date <= end_date)
    
    # Category filter
    if category:
        query = query.filter(models.Expense.category == category)
    
    # Order by date (newest first)
    expenses = query.order_by(models.Expense.date.desc()).all()
    
    return expenses

# ========== GET SINGLE EXPENSE ==========

@router.get("/{expense_id}", response_model=schemas.ExpenseResponse)
def get_expense(
    expense_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get single expense by ID
    
    Only returns if expense belongs to current user
    """
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    return expense

# ========== UPDATE EXPENSE ==========

@router.put("/{expense_id}", response_model=schemas.ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_update: schemas.ExpenseUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update expense
    
    Only updates if expense belongs to current user
    Partial update - only provided fields are updated
    """
    # Find expense
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Update only provided fields
    update_data = expense_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(expense, key, value)
    
    db.commit()
    db.refresh(expense)
    
    return expense

# ========== DELETE EXPENSE ==========

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete expense
    
    Only deletes if expense belongs to current user
    """
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    db.delete(expense)
    db.commit()
    
    return None

# ========== GET SUMMARY ==========

@router.get("/summary/stats", response_model=schemas.ExpenseSummary)
def get_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get expense summary by category
    
    Returns total amount and count per category
    """
    # Base query
    query = db.query(
        models.Expense.category,
        func.sum(models.Expense.amount).label('total'),
        func.count(models.Expense.id).label('count')
    ).filter(
        models.Expense.user_id == current_user.id
    )
    
    # Date filters
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    
    if end_date:
        query = query.filter(models.Expense.date <= end_date)
    
    # Group by category
    results = query.group_by(models.Expense.category).all()
    
    # Calculate totals
    total_amount = sum(r.total for r in results)
    total_count = sum(r.count for r in results)
    
    # Format category summaries
    categories = [
        schemas.CategorySummary(
            category=r.category,
            total=r.total,
            count=r.count
        )
        for r in results
    ]
    
    return schemas.ExpenseSummary(
        total_amount=total_amount,
        total_count=total_count,
        categories=categories
    )