from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from models import UserRole


# ==================== User/Auth Schemas ====================

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=256)
    confirm_password: str = Field(..., min_length=8, max_length=256)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data"""
    sub: str
    user_id: int
    role: UserRole
    exp: Optional[float] = None


# ==================== Entity Schemas ====================

class EntityBase(BaseModel):
    """Base entity schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    entity_type: Optional[str] = None


class EntityCreate(EntityBase):
    """Schema for creating entity"""
    pass


class EntityUpdate(BaseModel):
    """Schema for updating entity"""
    name: Optional[str] = None
    description: Optional[str] = None
    entity_type: Optional[str] = None
    is_active: Optional[bool] = None


class EntityResponse(EntityBase):
    """Schema for entity response"""
    id: int
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Transaction Schemas ====================

class TransactionBase(BaseModel):
    """Base transaction schema"""
    transaction_type: str = Field(..., min_length=1)  # "income" or "expense"
    amount: int = Field(..., gt=0)  # Amount 
    category: str = Field(..., min_length=1)
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Schema for creating transaction"""
    transaction_date: datetime


class TransactionUpdate(BaseModel):
    """Schema for updating transaction"""
    transaction_type: Optional[str] = None
    amount: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None


class TransactionResponse(TransactionBase):
    """Schema for transaction response"""
    id: int
    entity_id: int
    transaction_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Admin Schemas ====================

class AdminCreate(UserBase):
    """Schema for admin registration"""
    password: str = Field(..., min_length=8, max_length=100)


class AdminResponse(UserResponse):
    """Schema for admin response"""
    pass


class ClientResponse(UserResponse):
    """Schema for client response"""
    pass


class AdminActionResponse(BaseModel):
    """Schema for admin action response"""
    id: int
    admin_id: int
    action_type: str
    target_user_id: Optional[int] = None
    action_details: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminDashboardStats(BaseModel):
    """Schema for admin dashboard statistics"""
    total_users: int
    total_clients: int
    total_admins: int
    active_users: int
    inactive_users: int
    new_users_today: int
    recent_admin_actions: List[AdminActionResponse]


# ==================== Auth Payloads ====================

class PasswordChange(BaseModel):
    """Schema for password change"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
