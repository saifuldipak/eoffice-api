from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from src.models import ItemTypes, ItemTypeCreate, ItemTypeInfo, ItemBrandCreate, ItemBrandInfo, ItemBrands, ItemInfo, ItemCreate,  Requisitions, Users, RequisitionStatusUpdate, UserAction
from src.db_queries.requisitions import *
from src.dependency import get_session
from sqlalchemy.exc import IntegrityError
from typing import List
from src.models import ItemCreate, Items
from src.auth import get_current_user, check_authorization

router_requisitions = APIRouter(
    prefix="/requisitions", 
    tags=["requisitions"], 
    dependencies=[
        Depends(get_session), 
        Depends(lambda: check_authorization(UserAction.MANAGE_REQUISITION))
        ]
)
router_requisition_items = APIRouter(
    prefix="/requisition/items",
    tags=["requisition_items"],
    dependencies=[
        Depends(get_session),
        Depends(lambda: check_authorization(UserAction.MANAGE_REQUISITION_ITEM))
    ]
)

@router_requisition_items.post("/types/", response_model=ItemTypeInfo)
def create_item_type(item_type_data: ItemTypeCreate, db: Session = Depends(get_session)):
    """
    Create a new item type in the database.
    """
    try:
        db_item_type = ItemTypes(**item_type_data.model_dump())
        return add_item_type_to_db(db, db_item_type)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Item type already exists or item type value is not string")

@router_requisition_items.patch("/types/{type_id}", response_model=ItemTypeInfo)
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

@router_requisition_items.delete("/types/{type_id}")
def delete_item_type(type_id: int, db: Session = Depends(get_session)):
    """
    Delete an existing item type from the database.
    """
    existing_item_type = get_item_type_by_id(db, type_id)
    if not existing_item_type:
        raise HTTPException(status_code=404, detail="Item type not found")
    
    try:
        delete_item_type_from_db(db, type_id)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Cannot delete item type as it is referenced by other records")

@router_requisition_items.post("/brands/", response_model=ItemBrandInfo)
def create_item_brand(brand_data: ItemBrandCreate, db: Session = Depends(get_session)):
    """
    Create a new item brand in the database.
    """
    try:
        db_brand = ItemBrands(**brand_data.model_dump())
        return add_item_brand_to_db(db, db_brand)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Item brand already exists or brand value is not string")

@router_requisition_items.patch("/brands/{brand_id}", response_model=ItemBrandInfo)
def update_item_brand(brand_id: int, brand_data: ItemBrandInfo, db: Session = Depends(get_session)):
    """
    Update an existing item brand in the database.
    """
    existing_brand = get_item_brand_by_id(db, brand_id)
    if not existing_brand:
        raise HTTPException(status_code=404, detail="Item brand not found")
    
    try:
        updated = update_item_brand_in_db(db, brand_data)
        return updated
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Item brand already exists or brand value is not string")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router_requisition_items.delete("/brands/{brand_id}")
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

@router_requisition_items.post("/items/", response_model=ItemInfo)
def create_item(item: ItemCreate, db: Session = Depends(get_session)):
    # Verify the item type exists
    item_type_obj = get_item_type_by_id(db, item.type)
    if not item_type_obj:
        raise HTTPException(status_code=404, detail="Item type not found")
    
    # Verify the item brand exists if a brand id is provided
    if item.brand is not None:
        brand_obj = get_item_brand_by_id(db, item.brand)
        if not brand_obj:
            raise HTTPException(status_code=404, detail="Item brand not found")
    
    db_item = Items(**item.model_dump())
    try:
        return create_item_in_db(db, db_item)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Error creating item: model already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router_requisition_items.get("/items/{item_id}", response_model=ItemInfo)
def get_item(item_id: int, db: Session = Depends(get_session)):
    item = get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router_requisition_items.get("/items/", response_model=List[ItemInfo])
def list_items(db: Session = Depends(get_session)):
    return get_item_list_from_db(db)

@router_requisition_items.patch("/items/{item_id}", response_model=ItemInfo)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_session)):
    existing_item = get_item_by_id(db, item_id)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check for valid item type and brand in the update data
    if item.type:
        item_type_obj = get_item_type_by_id(db, item.type)
        if not item_type_obj:
            raise HTTPException(status_code=404, detail="Item type not found")
    if item.brand is not None:
        brand_obj = get_item_brand_by_id(db, item.brand)
        if not brand_obj:
            raise HTTPException(status_code=404, detail="Item brand not found")
    
    updated_item = Items(id=item_id, **item.model_dump())
    try:
        return update_item_in_db(db, updated_item)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Error updating item: model already exists")
    except ValueError as e: 
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router_requisition_items.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_session)):
    deleted = delete_item_from_db(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": f"Item {item_id} successfully deleted"}

@router_requisitions.post("/requisitions/", response_model=Requisitions)
def create_requisition(req: Requisitions, db: Session = Depends(get_session)):
    try:
        return create_requisition_in_db(db, req)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Failed to create requisition due to integrity error")

@router_requisitions.get("/requisitions/{req_id}", response_model=Requisitions)
def read_requisition(req_id: int, db: Session = Depends(get_session)):
    req = get_requisition_by_id(db, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Requisition not found")
    return req

@router_requisitions.get("/requisitions/", response_model=List[Requisitions])
def list_requisitions(db: Session = Depends(get_session)):
    return get_all_requisitions(db)

@router_requisitions.patch("/requisitions/{req_id}", response_model=Requisitions)
def update_requisition(requisition_id: int, requisition_status: RequisitionStatusUpdate, user: Users = Depends(get_current_user), db: Session = Depends(get_session)):
    if user.id is None:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    try:
        return update_requisition_in_db(db, requisition_id, requisition_status, user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Update failed due to integrity constraints")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router_requisitions.delete("/requisitions/{requisition_id}")
def delete_requisition(requisition_id: int, db: Session = Depends(get_session)):
    try:
        message = delete_requisition_from_db(db, requisition_id)
        return {"message": message}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Cannot delete requisition as it is referenced by other records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


