from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from models import User, UserRole
from schemas import UserCreate, UserLogin, Token, UserResponse
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["authentication"])



def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new client user.
    
    - **email**: User's email address (must be unique)
    - **username**: Username (must be unique, 3-50 characters)
    - **full_name**: Optional full name
    - **password**: Password (minimum 8 characters)
    """
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )
    
    # Create new user
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        role=UserRole.CLIENT,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and receive JWT tokens.
    
    - **email**: User's email address
    - **password**: User's password
    """
    
    # Find user by email
    db_user = db.query(User).filter(User.email == credentials.email).first()
    
    if not db_user or not verify_password(credentials.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Create tokens
    access_token = create_access_token(
        user_id=db_user.id,
        email=db_user.email,
        role=db_user.role,
    )
    refresh_token = create_refresh_token(
        user_id=db_user.id,
        email=db_user.email,
        role=db_user.role,
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh_token(current_user: User = Depends(get_db)):
    """
    Refresh access token using refresh token.
    
    **Note**: This is simplified - in production, you should validate the refresh token properly.
    """
    
    access_token = create_access_token(
        user_id=current_user.id,
        email=current_user.email,
        role=current_user.role,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
