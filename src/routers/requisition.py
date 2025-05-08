from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from src.models import Items, ItemTypes, ItemTypeCreate, ItemTypeInfo
from src.db_queries import add_item_to_db, add_item_type_to_db
from src.dependency import get_session
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/requisition")

@router.post("/item-types/", response_model=ItemTypeInfo)
def create_item_type(item_type_data: ItemTypeCreate, db: Session = Depends(get_session)):
    """
    Create a new item type in the database.

    Args:
        item_type_data (ItemTypes): The item type details to be added.
        db (Session): The database session.

    Returns:
        ItemTypes: The newly created item type object.
    """

    try:
        db_item_type = ItemTypes(**item_type_data.model_dump())
        return add_item_type_to_db(db, db_item_type)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Item type already exists or item type value is not string")
    

@router.post("/items/", response_model=Items)
def create_item(item_data: Items, db: Session = Depends(get_session)):
    """
    Create a new item in the database.

    Args:
        item_data (Items): The item details to be added.
        db (Session): The database session.

    Returns:
        Items: The newly created item object.
    """
    try:
        return add_item_to_db(db, item_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))