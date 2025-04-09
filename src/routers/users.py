from fastapi import HTTPException, Depends, APIRouter
from typing import List
import logging
from sqlmodel import Session
from src.dependency import get_session
from src.auth import get_user_admin
from src.db_queries import create_user_in_db, get_users_from_db, delete_user_from_db, update_user_in_db 
from src.models import UserCreate, UserInfo, UserUpdate  
from sqlalchemy.exc import IntegrityError

# Configure logger
logger = logging.getLogger("users_router")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_user_admin)]
)

@router.post("/", response_model=UserInfo)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    try:
        db_user = create_user_in_db(session, user)
        return db_user
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")

@router.get("/{username}", response_model=List[UserInfo])
async def get_users(username: str, session: Session = Depends(get_session)):
    results = get_users_from_db(session, username)
    if not results:
        raise HTTPException(status_code=404, detail="No users found")
    return results

@router.delete("/{username}")
async def delete_user(username: str, session: Session = Depends(get_session)):
    db_user = delete_user_from_db(session, username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {username} successfully deleted"}

@router.patch("/{username}", response_model=UserInfo)
async def update_user(username: str, user_update: UserUpdate, session: Session = Depends(get_session)):
    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400, 
            detail="No valid fields to update"
        )
    
    try:
        db_user = update_user_in_db(session, username, update_data)  # Use the update_user_in_db function
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Update failed due to integrity constraints (e.g., duplicate username or email)"
        )

