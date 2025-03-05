from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from sqlmodel import create_engine
import bcrypt
from sqlalchemy import UniqueConstraint

class UserBase(SQLModel):
    username: str = Field(sa_column_kwargs={"unique": True})
    first_name: str
    last_name: str
    email: str = Field(sa_column_kwargs={"unique": True})

class UserCreate(UserBase):
    password: str

class Users(UserCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_active: bool
    group_id: int | None = Field(default=None, foreign_key="groups.id")
    created_at: datetime
    updated_at: datetime

    __table_args__ = (UniqueConstraint("username", "email", name="uix_username_email"),)

class UserInfo(UserBase):
    id: int
    is_active: bool
    group_id: int | None
    created_at: datetime
    updated_at: datetime  

class GroupCreate(SQLModel):
    name: str = Field(sa_column_kwargs={"unique": True})
    description: str | None = None

class Groups(GroupCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime

class GroupInfo(GroupCreate):
    id: int
    created_at: datetime
    updated_at: datetime

class AccessTypeCreate(SQLModel):
    type: str = Field(sa_column_kwargs={"unique": True})
    description: str | None = None

class AccessTypes(AccessTypeCreate, table=True):
    __tablename__ = "access_types"
    id: int | None = Field(default=None, primary_key=True)

class AccessTypeInfo(AccessTypeCreate):
    id: int

class GroupAccess(SQLModel, table=True):
    group_id: int = Field(primary_key=True, foreign_key="groups.id")
    access_type_id: int = Field(primary_key=True, foreign_key="access_types.id")

class GroupAccessInfo(SQLModel):
    group_name: str
    access_type: str
    
def create_db_connection():
    db_url = f"sqlite:///./eoffice.db"
    engine = create_engine(db_url, echo=True, connect_args={"check_same_thread": False})
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
