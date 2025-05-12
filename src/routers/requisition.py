from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from src.models import ItemTypes, ItemTypeCreate, ItemTypeInfo, ItemBrandCreate, ItemBrandInfo, ItemBrands
from src.db_queries import add_item_type_to_db, get_item_type_by_id, update_item_type_in_db, delete_item_type_from_db, add_item_brand_to_db, get_item_brand_by_id, update_item_brand_in_db, delete_item_brand_from_db
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

@router.delete("/item-types/{item_type_id}")
def delete_item_type(item_type_id: int, db: Session = Depends(get_session)):
    """
    Delete an existing item type from the database.
    """
    existing_item_type = get_item_type_by_id(db, item_type_id)
    if not existing_item_type:
        raise HTTPException(status_code=404, detail="Item type not found")
    
    try:
        delete_item_type_from_db(db, item_type_id)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Cannot delete item type as it is referenced by other records")

@router.post("/item-brands/", response_model=ItemBrandInfo)
def create_item_brand(item_brand_data: ItemBrandCreate, db: Session = Depends(get_session)):
    """
    Create a new item brand in the database.
    """
    try:
        db_item_brand = ItemBrands(**item_brand_data.model_dump())
        return add_item_brand_to_db(db, db_item_brand)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Item brand already exists or brand value is not string")

@router.patch("/item-brands/{brand_id}", response_model=ItemBrandInfo)
def update_item_brand(brand_id: int, item_brand_data: ItemBrandInfo, db: Session = Depends(get_session)):
    """
    Update an existing item brand in the database.
    """
    existing_brand = get_item_brand_by_id(db, brand_id)
    if not existing_brand:
        raise HTTPException(status_code=404, detail="Item brand not found")
    
    try:
        updated = update_item_brand_in_db(db, item_brand_data)
        return updated
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Item brand already exists or brand value is not string")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/item-brands/{brand_id}")
def delete_item_brand(brand_id: int, db: Session = Depends(get_session)):
    """
    Delete an existing item brand from the database.
    """
    existing_brand = get_item_brand_by_id(db, brand_id)
    if not existing_brand:
        raise HTTPException(status_code=404, detail="Item brand not found")
    
    try:
        delete_item_brand_from_db(db, brand_id)
        return {"message": f"Item brand {brand_id} successfully deleted"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Cannot delete item brand as it is referenced by other records")
