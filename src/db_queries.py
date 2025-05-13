from sqlmodel import Session, select
from src.models import Users, Teams, TeamUpdate, UserCreate, Items, ItemTypes, ItemTypeInfo, ItemBrands, ItemBrandInfo, Items
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from passlib.context import CryptContext
from src.models import ItemTypes, ItemTypeInfo, ItemBrands, ItemBrandInfo, Items
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user_in_db(session: Session, user_data: UserCreate) -> Users:
    db_user = Users(**user_data.model_dump())
    db_user.password = hash_password(user_data.password)
    db_user.is_active = True
    db_user.created_at = datetime.now()
    db_user.updated_at = datetime.now()


    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError:
        session.rollback()
        raise

def get_users_from_db(session: Session, username: str):
    statement = select(Users).where(Users.username.like(f"{username}%"))
    return session.exec(statement).all()

def delete_user_from_db(session: Session, username: str):
    statement = select(Users).where(Users.username == username)
    db_user = session.exec(statement).first()
    if db_user:
        session.delete(db_user)
        session.commit()
    return db_user

def update_user_in_db(session: Session, username: str, updated_data: dict) -> Users:
    statement = select(Users).where(Users.username == username)
    db_user = session.exec(statement).first()
    if not db_user:
        raise ValueError(f"User with username {username} not found")

    for key, value in updated_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    db_user.updated_at = datetime.now()

    try:
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError:
        #logger.error(f"{str(e)}")
        session.rollback()
        raise
    except Exception as e:
        #logger.error(f"{str(e)}")
        session.rollback()
        raise e

# --- CRUD operations for Teams ---

def create_team_in_db(session: Session, db_team_data: Teams):    
    session.add(db_team_data)
    try:
        session.commit()
        session.refresh(db_team_data)
        return db_team_data
    except IntegrityError:
        session.rollback()
        raise

def get_team_by_name_from_db(session: Session, team_name: str) -> Teams | None:
    statement = select(Teams).where(Teams.name == team_name)
    return session.exec(statement).first()

def update_team_in_db(session: Session, team_update_data: TeamUpdate) -> Teams | None:
    statement = select(Teams).where(Teams.name == team_update_data.name)
    db_team = session.exec(statement).first()
    if not db_team:
        raise ValueError(f"Team with name {team_update_data.name} not found")

    db_team.description = team_update_data.description

    try:
        session.commit()
        session.refresh(db_team)
        return db_team
    except Exception as e:
        session.rollback()
        raise e 

def delete_team_from_db(session: Session, team_name: str):
    statement = select(Teams).where(Teams.name == team_name)
    db_team = session.exec(statement).first()
    if not db_team:
        raise ValueError(f"Team with name {team_name} not found")
    
    try:
        session.delete(db_team)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise e
    
    return db_team

def get_team_list_from_db(session: Session):
    statement = select(Teams)
    return session.exec(statement).all()

def add_item_type_to_db(session: Session, db_item_type: ItemTypes):
    """
    Add a new item type to the database.

    Args:
        session (Session): The database session.
        item_type_data (ItemTypes): An instance of the ItemTypes class containing item type details.

    Returns:
        ItemTypes: The newly created item type object.
    """
    session.add(db_item_type)
    try:
        session.commit()
        session.refresh(db_item_type)
        return db_item_type
    except IntegrityError as e:
        session.rollback()
        raise e

def get_item_type_by_id(session: Session, type_id: int) -> Optional[ItemTypes]:
    """
    Retrieve an item type from the database by its ID.

    Args:
        session (Session): The database session.
        type_id (int): The ID of the item type.

    Returns:
        Optional[ItemTypes]: The item type object if found, otherwise None.
    """
    try:
        statement = select(ItemTypes).where(ItemTypes.id == type_id)
        return session.exec(statement).first()
    except IntegrityError as e:
        session.rollback()
        raise e

def update_item_type_in_db(session: Session, updated_item_type: ItemTypeInfo) -> Optional[ItemTypes]:
    """
    Update an item type details using the provided ItemTypes object.

    Args:
        session (Session): The database session.
        updated_item_type (ItemTypes): An instance of ItemTypes with updated details. The id attribute is used to find the record.

    Returns:
        Optional[ItemTypes]: The updated item type object, or None if the item type does not exist.
    """
    # Retrieve the existing record by id
    statement = select(ItemTypes).where(ItemTypes.id == updated_item_type.id)
    db_item_type = session.exec(statement).first()
    if not db_item_type:
        raise ValueError(f"ItemType with id {updated_item_type.id} does not exist.")

    # Update the fields from the provided ItemTypes object
    for key, value in updated_item_type.__dict__.items():
        # Skip SQLModel internal attributes and primary key
        if key.startswith("_") or key == "id":
            continue
        setattr(db_item_type, key, value)

    try:
        session.commit()
        session.refresh(db_item_type)
        return db_item_type
    except IntegrityError as e:
        session.rollback()
        raise e

def delete_item_type_from_db(session: Session, type_id: int) -> None:
    """
    Delete an item type from the database by its ID.

    Args:
        session (Session): The database session.
        type_id (int): The ID of the item type to delete.

    Returns:
        Optional[ItemTypes]: The deleted item type object if found and deleted, otherwise None.
    """
    statement = select(ItemTypes).where(ItemTypes.id == type_id)
    db_item_type = session.exec(statement).first()
    if db_item_type:
        session.delete(db_item_type)
        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise e
    
    return None

def add_item_brand_to_db(session: Session, item_brand: ItemBrands) -> ItemBrands:
    session.add(item_brand)
    try:
        session.commit()
        session.refresh(item_brand)
        return item_brand
    except IntegrityError as e:
        session.rollback()
        raise e

def get_item_brand_by_id(session: Session, brand_id: int) -> Optional[ItemBrands]:
    statement = select(ItemBrands).where(ItemBrands.id == brand_id)
    return session.exec(statement).first()

def update_item_brand_in_db(session: Session, updated_brand: ItemBrandInfo) -> Optional[ItemBrands]:
    statement = select(ItemBrands).where(ItemBrands.id == updated_brand.id)
    db_brand = session.exec(statement).first()
    if not db_brand:
        raise ValueError(f"ItemBrand with id {updated_brand.id} does not exist.")
    for key, value in updated_brand.__dict__.items():
        if key.startswith("_") or key == "id":
            continue
        setattr(db_brand, key, value)
    try:
        session.commit()
        session.refresh(db_brand)
        return db_brand
    except IntegrityError as e:
        session.rollback()
        raise e

def delete_item_brand_from_db(session: Session, brand_id: int) -> None:
    statement = select(ItemBrands).where(ItemBrands.id == brand_id)
    db_brand = session.exec(statement).first()
    if db_brand:
        session.delete(db_brand)
        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise e
    return None

def create_item_in_db(session: Session, db_item_data: Items) -> Items:
    session.add(db_item_data)
    try:
        session.commit()
        session.refresh(db_item_data)
        return db_item_data
    except IntegrityError as e:
        session.rollback()
        raise e

def get_item_by_id(session: Session, item_id: int) -> Optional[Items]:
    statement = select(Items).where(Items.id == item_id)
    return session.exec(statement).first()

def get_items_from_db(session: Session) -> list[Items]:
    statement = select(Items)
    return session.exec(statement).all()

def update_item_in_db_by_id(session: Session, db_updated_item_data: Items) -> Optional[Items]:
    db_item = get_item_by_id(session, db_updated_item_data.id)
    if not db_item:
        raise ValueError(f"Item with id {db_updated_item_data.id} does not exist.")
    
    for key, value in db_updated_item_data.__dict__.items():
        if key.startswith("_") or key == "id":
            continue
        setattr(db_item, key, value)
    
    try:
        session.commit()
        session.refresh(db_item)
        return db_item
    except IntegrityError as e:
        session.rollback()
        raise e

def delete_item_from_db(session: Session, item_id: int) -> Optional[Items]:
    db_item = get_item_by_id(session, item_id)
    if db_item:
        session.delete(db_item)
        try:
            session.commit()
            return db_item
        except IntegrityError as e:
            session.rollback()
            raise e
    return None

