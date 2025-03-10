from fastapi import HTTPException, Depends, APIRouter
from sqlmodel import Session, select
from src.models import Users, UserCreate, UserInfo, UserUpdate
import bcrypt
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.dependency import get_session
import logging
from src.auth import get_user_admin

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_user_admin)]
)

@router.post("/", response_model=UserInfo)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db_user = Users(
        username=user.username,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.role,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
    except IntegrityError as e:
        session.rollback()
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail="User with this username or email already exists")
    return db_user

@router.get("/{username}", response_model=UserInfo)
async def get_user_by_username(username: str, session: Session = Depends(get_session)):
    statement = select(Users).where(Users.username == username)
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@router.delete("/{username}")
async def delete_user(username: str, session: Session = Depends(get_session)):
    statement = select(Users).where(Users.username == username)
    db_user = session.exec(statement).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        session.delete(db_user)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while deleting user")
    
    return {"message": f"User {username} successfully deleted"}

@router.patch("/{username}", response_model=UserInfo)
async def update_user(
    username: str, 
    user_update: UserUpdate, 
    session: Session = Depends(get_session)
):
    statement = select(Users).where(Users.username == username)
    db_user = session.exec(statement).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400, 
            detail="No valid fields to update"
        )
    
    try:
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db_user.updated_at = datetime.now()
        
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except IntegrityError as e:
        session.rollback()
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(
            status_code=400, 
            detail="User with this email already exists"
        )
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error occurred while updating user"
        )
    
    return db_user


""" @router.post("/groups", response_model=GroupInfo)
async def create_group(group: GroupCreate, session: Session = Depends(get_session)):
    db_group = Groups(
        name=group.name, 
        description=group.description,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(db_group)
    try:
        session.commit()
        session.refresh(db_group)
    except IntegrityError as e:
        session.rollback()
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail="Group with this name already exists")
    return db_group

@router.post("/access-types", response_model=AccessTypeInfo)
async def create_access_type(access_type: AccessTypeCreate, session: Session = Depends(get_session)):
    db_access_type = AccessTypes(
        type=access_type.type,
        description=access_type.description
    )
    session.add(db_access_type)
    try:
        session.commit()
        session.refresh(db_access_type)
    except IntegrityError as e:
        session.rollback()
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail="Access type with this name already exists")
    return db_access_type

@router.post("/group-access", response_model=GroupAccess)
async def create_group_access(group_access: GroupAccessInfo, session: Session = Depends(get_session)):
    statement = select(Groups).where(Groups.name == group_access.group_name)
    db_group = session.exec(statement).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    statement = select(AccessTypes).where(AccessTypes.type == group_access.access_type)
    db_access_type = session.exec(statement).first()
    if not db_access_type:
        raise HTTPException(status_code=404, detail="Access type not found")
    
    db_group_access = GroupAccess(
        group_id=db_group.id,
        access_type_id=db_access_type.id
    )
  
    session.add(db_group_access)
    try:
        session.commit()
        session.refresh(db_group_access)
    except IntegrityError as e:
        session.rollback()
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail="Group access with this group name and access type already exists")
    return db_group_access """

