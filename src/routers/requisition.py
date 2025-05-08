from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from src.models import Items, ItemTypes, ItemTypeCreate, ItemTypeInfo
from src.db_queries import add_item_to_db, add_item_type_to_db, get_item_type_by_id, update_item_type_in_db
from src.dependency import get_session
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/requisition")

@router.post("/item-types/", response_model=ItemTypeInfo)
def create_item_type(item_type_data: ItemTypeCreate, db: Session = Depends(get_session)):
    """
    Create a new item type in the database.
    """
    try:
        db_item_type = ItemTypes(**item_type_data.model_dump())
        return add_item_type_to_db(db, db_item_type)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Item type already exists or item type value is not string")

@router.patch("/item-types/{type_id}", response_model=ItemTypeInfo)
def update_item_type(type_id: int, item_type_data: ItemTypeInfo, db: Session = Depends(get_session)):
    """
    Update an existing item type in the database.
    """
    existing_item_type = get_item_type_by_id(db, type_id)
    if not existing_item_type:
        raise HTTPException(status_code=404, detail="Item type not found")
    
    try:
        updated = update_item_type_in_db(db, item_type_data)
        return updated
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Item type already exists or item type value is not string")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
