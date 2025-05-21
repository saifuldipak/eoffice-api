from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from src.models import ItemTypes, ItemTypeInfo,ItemBrands, ItemBrandInfo, Items, ItemInfo, Requisitions, RequisitionStatus
from datetime import datetime

def add_item_type_to_db(session: Session, item_type: ItemTypes) -> ItemTypes:
    try:
        session.add(item_type)
        session.commit()
        session.refresh(item_type)
        return item_type
    except IntegrityError:
        session.rollback()
        raise
    except Exception:
        session.rollback()
        raise

def get_item_type_by_id(db: Session, type_id: int) -> ItemTypes | None:
    statement = select(ItemTypes).where(ItemTypes.id == type_id)

    try:
        return db.exec(statement).first() 
    except Exception:
        raise 

def update_item_type_in_db(db: Session, item_type_data: ItemTypeInfo) -> ItemTypes:
    statement = select(ItemTypes).where(ItemTypes.id == item_type_data.id)
    item_type_db = db.exec(statement).first()
    if not item_type_db:
        raise ValueError("Item type {item_type_data.id} not found for update")

    update_data = item_type_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item_type_db, key, value)
    
    try:
        db.commit()
        db.refresh(item_type_db)
        return item_type_db
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


def delete_item_type_from_db(db: Session, item_type_id: int) -> str:
    statement = select(ItemTypes).where(ItemTypes.id == item_type_id)
    item_type_db = db.exec(statement).first()
    if not item_type_db:
        raise ValueError("Item type {item_type_id} not found for deletion")
    
    try:
        db.delete(item_type_db)
        db.commit()
        return f"Item type {item_type_id} deleted successfully"
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

def add_item_brand_to_db(db: Session, item_brand: ItemBrands) -> ItemBrands:
    try:
        db.add(item_brand)
        db.commit()
        db.refresh(item_brand)
        return item_brand
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

def get_item_brand_by_id(db: Session, brand_id: int) -> ItemBrands | None:
    statement = select(ItemBrands).where(ItemBrands.id == brand_id)
    try:
        return db.exec(statement).first()
    except Exception:
        raise

def update_item_brand_in_db(db: Session, item_brand_data: ItemBrandInfo) -> ItemBrands:
    statement = select(ItemBrands).where(ItemBrands.id == item_brand_data.id)
    item_brand_db = db.exec(statement).first()
    if not item_brand_db:
        raise ValueError("Item brand {item_brand_data.id} not found for update")
    
    update_data = item_brand_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item_brand_db, key, value)
    
    try:
        db.commit()
        db.refresh(item_brand_db)
        return item_brand_db
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

def delete_item_brand_from_db(db: Session, item_brand_id: int) -> str:
    statement = select(ItemBrands).where(ItemBrands.id == item_brand_id)
    item_brand_db = db.exec(statement).first()
    if not item_brand_db:
        raise ValueError("Item brand {brand_id} not found for deletion")
    
    try:
        db.delete(item_brand_db)
        db.commit()
        return f"Item brand {item_brand_id} deleted successfully"
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

def create_item_in_db(db: Session, item: Items) -> Items:
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


def get_item_by_id(db: Session, item_id: int) -> Items | None:
    statement = select(Items).where(Items.id == item_id)
    try:
        return db.exec(statement).first()
    except Exception:
        raise

def get_item_list_from_db(db: Session) -> list[Items] | None:
   statment = select(Items)
   try:
       return list(db.exec(statment).all())
   except Exception:
       raise

def update_item_in_db(db: Session, updated_item: Items) -> Items:
    statement = select(Items).where(Items.id == updated_item.id)
    existing_item = db.exec(statement).first()
    if not existing_item:
        raise ValueError(f"Item with Id {updated_item.id} not found")

    update_data = updated_item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_item, key, value)

    try:
        db.commit()
        db.refresh(existing_item)
        return existing_item
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

def delete_item_from_db(db: Session, item_id: int) -> str:
    statment = select(Items).where(Items.id == item_id)
    item = db.exec(statment).first()
    if not item:
        raise ValueError(f"Item with Id {item_id} not found for deletion")
    
    try:
        db.delete(item)
        db.commit()
        return f"Item with Id {item_id} deleted successfully"
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

def create_requisition_in_db(db: Session, requisition: Requisitions) -> Requisitions:
    try:
        db.add(requisition)
        db.commit()
        db.refresh(requisition)
        return requisition
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

def get_requisition_by_id(db: Session, req_id: int) -> Requisitions | None:
    statement = select(Requisitions).where(Requisitions.id == req_id)
    try:
        return db.exec(statement).first()
    except Exception:
        raise

def get_all_requisitions(db: Session) -> list[Requisitions] | None:
    statement = select(Requisitions)
    try:
        return list(db.exec(statement).all())
    except Exception:
        raise

def update_requisition_in_db(db: Session, requisition_id: int, requisition_status: str, user_id: int) -> Requisitions:
    statement = select(Requisitions).where(Requisitions.id == requisition_id)
    requisition_db = db.exec(statement).first()
    if not requisition_db:
        raise ValueError("Requisition with Id {requisition_id} not found")
    
    if requisition_status == 'approved':
        requisition_db.status = RequisitionStatus.APPROVED
        requisition_db.approval_date = datetime.now()
        requisition_db.approved_by = user_id
    elif requisition_status == 'delivered':
        requisition_db.status = RequisitionStatus.DELIVERED
        requisition_db.delivery_date = datetime.now()
        requisition_db.delivered_by = user_id
    else:
        raise ValueError("Invalid requisition status")

    try:
        db.commit()
        db.refresh(requisition_db)
        return requisition_db
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
    
def delete_requisition_from_db(db: Session, requisition_id: int) -> str:
    statement = select(Requisitions).where(Requisitions.id == requisition_id)
    requisition_db = db.exec(statement).first()
    if not requisition_db:
        raise ValueError("Requisition with Id {requisition_id} not found for deletion")
    try:
        db.delete(requisition_db)
        db.commit()
        return f"Requisition with Id {requisition_id} deleted successfully"
    except IntegrityError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise