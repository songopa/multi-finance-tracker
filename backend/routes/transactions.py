from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from datetime import datetime

from database import get_db
from models import Transaction, Entity, TransactionCategory, TransactionType, User
from schemas import TransactionCreate, TransactionUpdate, TransactionResponse
from auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _get_entity_or_403(entity_id: int, current_user: User, db: Session) -> Entity:
    """Get entity and verify the current user owns it."""
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    if entity.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return entity


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new transaction on one of the user's entities."""
    _get_entity_or_403(data.entity_id, current_user, db)

    category = db.query(TransactionCategory).filter(TransactionCategory.id == data.category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Enforce that transaction type matches category type
    if category.type != data.transaction_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{category.name}' is type '{category.type}' but transaction is '{data.transaction_type}'",
        )

    transaction = Transaction(**data.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return db.query(Transaction).options(joinedload(Transaction.category)).filter(Transaction.id == transaction.id).first()


@router.get("/", response_model=list[TransactionResponse])
def list_transactions(
    entity_id: int = Query(..., description="Filter by entity"),
    type: Optional[TransactionType] = Query(None, description="Filter by income or expense"),
    category_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List transactions for an entity with optional filters."""
    _get_entity_or_403(entity_id, current_user, db)

    query = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.entity_id == entity_id)
    )

    if type:
        query = query.filter(Transaction.transaction_type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if date_from:
        query = query.filter(Transaction.transaction_date >= date_from)
    if date_to:
        query = query.filter(Transaction.transaction_date <= date_to)

    return query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single transaction by ID."""
    transaction = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.id == transaction_id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    _get_entity_or_403(transaction.entity_id, current_user, db)
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a transaction."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    _get_entity_or_403(transaction.entity_id, current_user, db)

    update_data = data.model_dump(exclude_unset=True)

    # If changing category, validate type compatibility
    new_category_id = update_data.get("category_id", transaction.category_id)
    new_type = update_data.get("transaction_type", transaction.transaction_type)

    if "category_id" in update_data or "transaction_type" in update_data:
        category = db.query(TransactionCategory).filter(TransactionCategory.id == new_category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        if category.type != new_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category type '{category.type}' doesn't match transaction type '{new_type}'",
            )

    for field, value in update_data.items():
        setattr(transaction, field, value)

    db.commit()

    return db.query(Transaction).options(joinedload(Transaction.category)).filter(Transaction.id == transaction_id).first()


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a transaction."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    _get_entity_or_403(transaction.entity_id, current_user, db)
    db.delete(transaction)
    db.commit()