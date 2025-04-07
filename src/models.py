import os
from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from sqlmodel import create_engine
import bcrypt
from sqlalchemy import UniqueConstraint
from enum import Enum

class UserRole(str, Enum):
    USER_ADMIN = "user_admin"
    TICKET_MANAGER = "ticket_manager"
    TICKET_UPDATER = "ticket_updater"

class UserBase(SQLModel):
    username: str = Field(sa_column_kwargs={"unique": True})
    first_name: str
    last_name: str
    email: str = Field(sa_column_kwargs={"unique": True})
    role: UserRole

class UserCreate(UserBase):
    password: str

class Users(UserCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    __table_args__ = (UniqueConstraint("username", "email", name="uix_username_email"),)

class UserInfo(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime 

class UserUpdate(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    role: UserRole | None = None
    password: str | None = None
    is_active: bool | None = None
    
def create_db_connection():
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./eoffice.db")  # Use DATABASE_URL env var, default to sqlite
    engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False})
    return engine

def recreate_tables(engine):
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)    

def create_admin_user():
    hashed_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
    user = Users(
        username='admin',
        password=hashed_password.decode('utf-8'),
        first_name='Admin',
        last_name='User',
        email='admin@eoffice',
        is_active=True,
        role='user_admin',
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    return user

if __name__ == '__main__':
    engine = create_db_connection()
    recreate_tables(engine)
    print('Tables recreated successfully')
    admin_user = create_admin_user()

    with Session(engine) as session:
        session.add(admin_user)
        session.commit()
        print('Admin user created successfully')
