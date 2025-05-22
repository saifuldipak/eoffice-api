from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from src.models import Users, RolePermissions, UserAction
from src.dependency import get_session
from sqlmodel import Session, select
from passlib.context import CryptContext

# to get a string like this run: openssl rand -hex 32
SECRET_KEY = "my-kothin-jotil-gopon-kotha"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

from typing import Optional

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user(username: str, password: str, session: Session):
    user = session.exec(select(Users).where(Users.username == username)).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user

async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found or has no role permissions",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or not isinstance(username, str):
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(Users).where(Users.username == username)).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_role_permissions(user: Users = Depends(get_current_user), session: Session = Depends(get_session)) -> list[RolePermissions]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found or has no role permissions",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user.role_id is None:
        raise credentials_exception
    
    role_permissions = session.exec(select(RolePermissions).where(RolePermissions.role_id == user.role_id)).all()
    if role_permissions is None:
        raise credentials_exception
    
    return list(role_permissions) 

async def check_manage_user_permission(current_user_role_permissions: list[RolePermissions] = Depends(get_role_permissions)) -> bool:
    has_permission = False
    for permission in current_user_role_permissions:
        if permission.permission == UserAction.MANAGE_USER:
            has_permission = True
            break
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions"
        )
    
    return has_permission

def check_authorization(access_permission: UserAction, role_permissions: list[RolePermissions] = Depends(get_role_permissions)) -> bool:
    has_permission = False
    for permission in role_permissions:
        if permission == access_permission:
            has_permission = True
            break
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions"
        )
    
    return has_permission