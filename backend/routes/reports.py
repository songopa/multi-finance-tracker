from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from database import get_db
from models import Transaction, Entity, TransactionCategory, TransactionType, User
from schemas import ReportResponse, CategoryBreakdown
from auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/", response_model=ReportResponse)
def get_report(
    entity_id: int = Query(..., description="Entity to report on"),
    date_from: Optional[datetime] = Query(None, description="Start date (inclusive)"),
    date_to: Optional[datetime] = Query(None, description="End date (inclusive)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a financial report for an entity.

    Returns income/expense totals, net balance, and per-category breakdown.
    Optionally filter by date range.
    """
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    if entity.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Base query filtered by date range
    base_query = db.query(Transaction).filter(Transaction.entity_id == entity_id)
    if date_from:
        base_query = base_query.filter(Transaction.transaction_date >= date_from)
    if date_to:
        base_query = base_query.filter(Transaction.transaction_date <= date_to)

    # Aggregate by category
    breakdown_query = (
        db.query(
            Transaction.category_id,
            TransactionCategory.name,
            TransactionCategory.type,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .join(TransactionCategory, Transaction.category_id == TransactionCategory.id)
        .filter(Transaction.entity_id == entity_id)
    )
    if date_from:
        breakdown_query = breakdown_query.filter(Transaction.transaction_date >= date_from)
    if date_to:
        breakdown_query = breakdown_query.filter(Transaction.transaction_date <= date_to)

    rows = breakdown_query.group_by(Transaction.category_id).all()

    income_breakdown = []
    expense_breakdown = []
    total_income = 0.0
    total_expenses = 0.0

    for row in rows:
        entry = CategoryBreakdown(
            category_id=row.category_id,
            category_name=row.name,
            type=row.type,
            total=round(row.total, 2),
            transaction_count=row.count,
        )
        if row.type == TransactionType.INCOME:
            income_breakdown.append(entry)
            total_income += row.total
        else:
            expense_breakdown.append(entry)
            total_expenses += row.total

    return ReportResponse(
        entity_id=entity.id,
        entity_name=entity.name,
        date_from=date_from,
        date_to=date_to,
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        net_balance=round(total_income - total_expenses, 2),
        income_breakdown=sorted(income_breakdown, key=lambda x: x.total, reverse=True),
        expense_breakdown=sorted(expense_breakdown, key=lambda x: x.total, reverse=True),
    )