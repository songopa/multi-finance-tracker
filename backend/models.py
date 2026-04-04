from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    CLIENT = "client"
    ADMIN = "admin"

class TransactionType(str, enum.Enum):
    """Transaction type enumeration"""
    INCOME = "income"
    EXPENSE = "expense"


class User(Base):
    """User model for both clients and admins"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    entities = relationship("Entity", back_populates="owner", cascade="all, delete-orphan")
    admin_actions = relationship("AdminAction", back_populates="admin", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class Entity(Base):
    """Financial entity model (personal, freelance project, small business, etc.)"""
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    entity_type = Column(String, nullable=True)  # e.g., "personal", "freelance", "business"
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="entities")
    transactions = relationship("Transaction", back_populates="entity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Entity(id={self.id}, name={self.name}, owner_id={self.owner_id})>"


class Transaction(Base):
    """Transaction model for income and expenses"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("transaction_categories.id"), nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), default=TransactionType.EXPENSE, nullable=False)
    amount = Column(Integer, nullable=False)  
    category_name = Column(String, nullable=False)  # e.g., "salary", "freelance", "food", "transport"
    description = Column(String, nullable=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    entity = relationship("Entity", back_populates="transactions")
    transaction_category = relationship("TransactionCategory", back_populates="transactions")
    def __repr__(self):
        return f"<Transaction(id={self.id}, entity_id={self.entity_id}, type={self.transaction_type})>"
    
class TransactionCategory(Base):
    __tablename__ = "transaction_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(Enum(TransactionType), nullable=False)  # Category type (income or expense)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="transaction_category")

class AdminAction(Base):
    """Admin audit log for tracking admin actions"""
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String, nullable=False)  # e.g., "user_created", "user_deactivated", "user_deleted"
    target_user_id = Column(Integer, nullable=True)  # User that the action was performed on
    action_details = Column(String, nullable=True)  # JSON details of the action
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    admin = relationship("User", back_populates="admin_actions")
    
    def __repr__(self):
        return f"<AdminAction(id={self.id}, admin_id={self.admin_id}, action_type={self.action_type})>"
