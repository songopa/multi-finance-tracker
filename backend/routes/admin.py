from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from database import get_db
from models import User, UserRole, AdminAction
from schemas import (
    AdminCreate,
    AdminResponse,
    ClientResponse,
    UserResponse,
    AdminDashboardStats,
    AdminActionResponse,
)
from auth import hash_password, get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard/stats", response_model=AdminDashboardStats)
def get_dashboard_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Get admin dashboard statistics.
    
    Returns overall system statistics and recent admin actions.
    """
    
    # Get user statistics
    total_users = db.query(User).count()
    total_clients = db.query(User).filter(User.role == UserRole.CLIENT).count()
    total_admins = db.query(User).filter(User.role == UserRole.ADMIN).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    inactive_users = db.query(User).filter(User.is_active == False).count()
    
    # Get new users today
    today = datetime.utcnow().date()
    new_users_today = (
        db.query(User)
        .filter(User.created_at >= datetime(today.year, today.month, today.day))
        .count()
    )
    
    # Get recent admin actions (last 10)
    recent_actions = (
        db.query(AdminAction)
        .order_by(AdminAction.created_at.desc())
        .limit(10)
        .all()
    )
    
    return AdminDashboardStats(
        total_users=total_users,
        total_clients=total_clients,
        total_admins=total_admins,
        active_users=active_users,
        inactive_users=inactive_users,
        new_users_today=new_users_today,
        recent_admin_actions=recent_actions,
    )


@router.get("/users", response_model=list[UserResponse])
def list_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    role: str = Query(None),
    is_active: bool = Query(None),
):
    """
    List all users with optional filtering.
    
    - **skip**: Number of users to skip (pagination)
    - **limit**: Number of users to return (max 100)
    - **role**: Filter by role (client or admin)
    - **is_active**: Filter by active status
    """
    
    query = db.query(User)
    
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}",
            )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Get a specific user by ID.
    """
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Deactivate a user account.
    """
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Cannot deactivate yourself
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )
    
    user.is_active = False
    db.add(user)
    
    # Log admin action
    admin_action = AdminAction(
        admin_id=current_admin.id,
        action_type="user_deactivated",
        target_user_id=user_id,
        action_details=json.dumps({"reason": "deactivated"}),
    )
    db.add(admin_action)
    
    db.commit()
    
    return {"message": f"User {user_id} has been deactivated"}


@router.put("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Activate a deactivated user account.
    """
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.is_active = True
    db.add(user)
    
    # Log admin action
    admin_action = AdminAction(
        admin_id=current_admin.id,
        action_type="user_activated",
        target_user_id=user_id,
    )
    db.add(admin_action)
    
    db.commit()
    
    return {"message": f"User {user_id} has been activated"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Delete a user account and all associated data.
    
    **Warning**: This action cannot be undone.
    """
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Cannot delete yourself
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    
    user_email = user.email
    
    # Log admin action before deletion
    admin_action = AdminAction(
        admin_id=current_admin.id,
        action_type="user_deleted",
        target_user_id=user_id,
        action_details=json.dumps({"email": user_email}),
    )
    db.add(admin_action)
    
    # Delete user (cascade will delete related entities)
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user_id} ({user_email}) has been deleted"}


@router.get("/actions", response_model=list[AdminActionResponse])
def list_admin_actions(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    days: int = Query(7, ge=1, le=365),
):
    """
    List recent admin actions for audit trail.
    
    - **skip**: Number of actions to skip (pagination)
    - **limit**: Number of actions to return (max 100)
    - **days**: Filter actions from the last N days
    """
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    actions = (
        db.query(AdminAction)
        .filter(AdminAction.created_at >= cutoff_date)
        .order_by(AdminAction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return actions
