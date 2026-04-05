from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from models import UserRole, TransactionType


# ==================== User/Auth Schemas ====================

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=256)
    confirm_password: str = Field(..., min_length=8, max_length=256)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: str
    user_id: int
    role: UserRole
    exp: Optional[float] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# ==================== Entity Schemas ====================

class EntityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    entity_type: Optional[str] = None

class EntityCreate(EntityBase):
    pass

class EntityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    entity_type: Optional[str] = None
    is_active: Optional[bool] = None

class EntityResponse(EntityBase):
    id: int
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ==================== Category Schemas ====================

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    type: TransactionType

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[TransactionType] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    type: TransactionType
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ==================== Transaction Schemas ====================

class TransactionCreate(BaseModel):
    entity_id: int
    category_id: int
    transaction_type: TransactionType
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    transaction_date: datetime

class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    transaction_type: Optional[TransactionType] = None
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None

class TransactionResponse(BaseModel):
    id: int
    entity_id: int
    category_id: int
    category: CategoryResponse
    transaction_type: TransactionType
    amount: float
    description: Optional[str]
    transaction_date: datetime
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ==================== Report Schemas ====================

class CategoryBreakdown(BaseModel):
    category_id: int
    category_name: str
    type: TransactionType
    total: float
    transaction_count: int

class ReportResponse(BaseModel):
    entity_id: int
    entity_name: str
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    total_income: float
    total_expenses: float
    net_balance: float
    income_breakdown: List[CategoryBreakdown]
    expense_breakdown: List[CategoryBreakdown]


# ==================== Admin Schemas ====================

class AdminCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class AdminResponse(UserResponse):
    pass

class ClientResponse(UserResponse):
    pass

class AdminActionResponse(BaseModel):
    id: int
    admin_id: int
    action_type: str
    target_user_id: Optional[int] = None
    action_details: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class AdminDashboardStats(BaseModel):
    total_users: int
    total_clients: int
    total_admins: int
    active_users: int
    inactive_users: int
    new_users_today: int
    recent_admin_actions: List[AdminActionResponse]
