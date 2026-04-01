from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Entity
from schemas import EntityCreate, EntityResponse
from auth import get_current_user

router = APIRouter(prefix="/entities", tags=["entities"])

@router.post("/", response_model=EntityResponse)
def create_entity(
    entity_data: EntityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new entity.
    
    - **name**: Name of the entity (must be unique)
    - **description**: Optional description of the entity
    """
    
    # Check if entity with the same name already exists
    existing_entity = db.query(Entity).filter(Entity.name == entity_data.name).first()
    
    if existing_entity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entity with this name already exists",
        )
    
    # Create new entity
    db_entity = Entity(
        name=entity_data.name,
        description=entity_data.description,
        owner_id=current_user.id,
    )
    
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    
    return db_entity

@router.get("/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """
    Get an entity by its ID.
    
    - **entity_id**: ID of the entity to retrieve
    """
    
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )
    
    return entity

@router.put("/{entity_id}", response_model=EntityResponse)
def update_entity(
    entity_id: int,
    entity_data: EntityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing entity.
    
    - **entity_id**: ID of the entity to update
    - **name**: Updated name of the entity (must be unique)
    - **description**: Updated description of the entity
    """
    
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )
    
    if entity.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this entity",
        )
    
    # Check if another entity with the same name exists
    existing_entity = db.query(Entity).filter(
        Entity.name == entity_data.name, Entity.id != entity_id
    ).first()
    
    if existing_entity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Another entity with this name already exists",
        )
    
    # Update entity fields
    entity.name = entity_data.name
    entity.description = entity_data.description
    
    db.add(entity)
    db.commit()
    db.refresh(entity)
    
    return entity