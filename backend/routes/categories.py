from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import TransactionCategory, TransactionType
from schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from auth import get_current_user
from models import User

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new transaction category."""
    existing = db.query(TransactionCategory).filter(TransactionCategory.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists",
        )

    category = TransactionCategory(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    type: Optional[TransactionType] = Query(None, description="Filter by income or expense"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all categories, optionally filtered by type."""
    query = db.query(TransactionCategory)
    if type:
        query = query.filter(TransactionCategory.type == type)
    return query.order_by(TransactionCategory.name).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single category by ID."""
    category = db.query(TransactionCategory).filter(TransactionCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a category."""
    category = db.query(TransactionCategory).filter(TransactionCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Check name uniqueness if name is changing
    if data.name and data.name != category.name:
        conflict = db.query(TransactionCategory).filter(TransactionCategory.name == data.name).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists",
            )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a category. Fails if transactions are using it."""
    category = db.query(TransactionCategory).filter(TransactionCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if category.transactions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category — {len(category.transactions)} transaction(s) are using it",
        )

    db.delete(category)
    db.commit()