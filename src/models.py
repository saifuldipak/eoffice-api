import os
from sqlmodel import SQLModel, Field, create_engine, Session, Column, ForeignKey
from datetime import datetime
from sqlalchemy import UniqueConstraint
from enum import Enum
import os
from datetime import datetime
import bcrypt
from dotenv import load_dotenv

class TeamBase(SQLModel):
    name: str = Field(sa_column_kwargs={"unique": True})
    description: str | None = None

class TeamCreate(TeamBase):
    pass

class Teams(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)    

class TeamInfo(TeamBase):
    id: int

class TeamUpdate(SQLModel):
    name: str 
    description: str 

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
    team_id: int | None = Field(default=None, sa_column=Column(ForeignKey("teams.id", ondelete="RESTRICT")))

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
    team_id: int | None = None
    
class RequisitionStatus(str, Enum):
    SUBMITTED = "submitted"
    APPROVED = "approved"
    DELIVERED = "delivered"    

class RequisitionUnit(str, Enum):
    PIECE = "piece"
    PAIR = "pair"
    METER = "meter"
    GRAM = "gram"

class Requisitions(SQLModel, table=True):
    __tablename__ = "requisition"
    id: int | None = Field(default=None, primary_key=True)
    status: RequisitionStatus
    submission_date: datetime
    approval_date: datetime | None = None
    delivery_date: datetime | None = None

class ItemTypeBase(SQLModel):
    item_type: str

class ItemTypeCreate(ItemTypeBase):
    pass

class ItemTypes(ItemTypeBase, table=True):
    __tablename__ = "item_types"
    id: int | None = Field(default=None, primary_key=True) 
    __table_args__ = (UniqueConstraint("item_type", name="uix_item_type"),)

class ItemTypeInfo(ItemTypeBase):
    id: int
    
class ItemBrands(SQLModel, table=True):
    __tablename__ = "item_brands"
    id: int | None = Field(default=None, primary_key=True)
    item_brand: str | None = Field(sa_column_kwargs={"unique": True})

class Items(SQLModel, table=True):
    __tablename__ = "items"
    id: int | None = Field(default=None, primary_key=True)
    type: int = Field(foreign_key="item_types.id") 
    brand: int | None = Field(default=None, foreign_key="item_brands.id")
    model: str | None = Field(default=None, sa_column_kwargs={"unique": True})

class CreateItem(SQLModel):
    type: str
    brand: int | None = None
    model: str | None = None

class RequisitionItems(SQLModel, table=True):
    __tablename__ = "requisition_items"
    id: int | None = Field(default=None, primary_key=True)
    requisition_id: int = Field(foreign_key="requisition.id")
    item_id: int = Field(foreign_key="items.id")
    unit: RequisitionUnit
    quantity: int
    delivery_date: datetime | None = None
    delivered_by: int | None = Field(foreign_key="users.id")

# Load environment variables from .env file
load_dotenv(override=True)

def create_db_connection():
    # Load DATABASE_URL from .env file, default to sqlite if not set
    db_url = os.getenv("DATABASE_URL", "sqlite:///./eoffice.db")
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