from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User, Entity
from schemas import EntityCreate, EntityUpdate, EntityResponse
from auth import get_current_user

router = APIRouter(prefix="/entities", tags=["entities"])


@router.post("/", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(
    data: EntityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(Entity).filter(
        Entity.name == data.name,
        Entity.owner_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have an entity with this name")

    entity = Entity(**data.model_dump(), owner_id=current_user.id)
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.get("/", response_model=list[EntityResponse])
def list_entities(
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Entity).filter(Entity.owner_id == current_user.id)
    if is_active is not None:
        query = query.filter(Entity.is_active == is_active)
    return query.order_by(Entity.created_at.desc()).all()


@router.get("/{entity_id}", response_model=EntityResponse)
def get_entity(
    entity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    if entity.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return entity


@router.put("/{entity_id}", response_model=EntityResponse)
def update_entity(
    entity_id: int,
    data: EntityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    if entity.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if data.name and data.name != entity.name:
        conflict = db.query(Entity).filter(
            Entity.name == data.name,
            Entity.owner_id == current_user.id,
            Entity.id != entity_id,
        ).first()
        if conflict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have an entity with this name")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)

    db.commit()
    db.refresh(entity)
    return entity


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entity(
    entity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    if entity.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db.delete(entity)
    db.commit()
