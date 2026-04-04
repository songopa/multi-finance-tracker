from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Transaction, TransactionCategory
from schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
    TransactionCategoryCreate,
    TransactionCategoryResponse,
)
from auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new transaction.
    
    - **transaction**: The transaction to create
    """
    
    db_transaction = Transaction(
        owner_id=current_user.id,
        entity_id=transaction.entity_id,
        category_id=transaction.category_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        category_name=transaction.category,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.get("/", response_model=list[TransactionResponse])
def get_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a list of all transactions for the current user.
    """
    
    transactions = db.query(Transaction).filter(Transaction.owner_id == current_user.id).all()
    
    return transactions

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a transaction by its ID.
    
    - **transaction_id**: ID of the transaction to retrieve
    """
    
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):
    """
    Update an existing transaction.
    
    - **transaction_id**: ID of the transaction to update
    - **transaction**: The updated transaction data
    """
    
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    if transaction.amount is not None:
        db_transaction.amount = transaction.amount
    if transaction.category is not None:
        db_transaction.category_name = transaction.category
    if transaction.transaction_date is not None:
        db_transaction.transaction_date = transaction.transaction_date
    if transaction.description is not None:
        db_transaction.description = transaction.description
    if transaction.transaction_type is not None:
        db_transaction.transaction_type = transaction.transaction_type
    
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a transaction by its ID.
    
    - **transaction_id**: ID of the transaction to delete
    """
    
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    db.delete(transaction)
    db.commit()

@router.post("/categories", response_model=TransactionCategoryResponse)
def create_transaction_category(
    category: TransactionCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new transaction category.
    
    - **category**: The transaction category to create
    """
    
    existing_category = db.query(TransactionCategory).filter(TransactionCategory.name == category.name).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists",
        )

    db_category = TransactionCategory(
        name=category.name,
        description=category.description,
        type=category.type,
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category


@router.get("/categories", response_model=list[TransactionCategoryResponse])
def get_transaction_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a list of all transaction categories.
    """
    
    categories = db.query(TransactionCategory).all()
    
    return categories

@router.put("/categories/{category_id}", response_model=TransactionCategoryResponse)
def update_transaction_category(
    category_id: int,
    category: TransactionCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing transaction category.
    
    - **category_id**: ID of the category to update
    - **category**: The updated category data
    """
    
    db_category = db.query(TransactionCategory).filter(TransactionCategory.id == category_id).first()
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    db_category.name = category.name
    db_category.description = category.description
    db_category.type = category.type
    
    db.commit()
    db.refresh(db_category)
    
    return db_category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a transaction category by its ID.
    
    - **category_id**: ID of the category to delete
    """
    
    category = db.query(TransactionCategory).filter(TransactionCategory.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    db.delete(category)
    db.commit()
