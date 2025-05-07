import os
import bcrypt
from sqlmodel import SQLModel, Field, create_engine, Session, text, Column, Integer, ForeignKey
from datetime import datetime
from sqlalchemy import UniqueConstraint
from enum import Enum
from dotenv import load_dotenv, find_dotenv  # Import dotenv

# Load environment variables from .env file
dotenv_path = find_dotenv()
if not dotenv_path:
    print("Warning: .env file is missing!")
else:
    load_dotenv(override=True)

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

class UserAction(str, Enum):
    MANAGE_USER = "manage_user"
    MANAGE_TICKET = "manage_ticket"
    UPDATE_TICKET = "update_ticket"

class RoleBase(SQLModel):
    name: str = Field(sa_column_kwargs={"unique": True})
    description: str | None = None

class Roles(RoleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class RoleCreate(RoleBase):
    pass

class RoleInfo(RoleBase):
    id: int

class RolePermissionBase(SQLModel):
    role_id: int = Field(sa_column=Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), primary_key=True))
    permission: UserAction = Field(primary_key=True)


class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermissions(RolePermissionBase, table=True):
    pass

class UserBase(SQLModel):
    username: str = Field(sa_column_kwargs={"unique": True})
    first_name: str
    last_name: str
    email: str = Field(sa_column_kwargs={"unique": True})
    team_id: int | None = Field(default=None, sa_column=Column(ForeignKey("teams.id", ondelete="RESTRICT")))
    role_id: int | None = Field(foreign_key="roles.id", ondelete="RESTRICT")

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
    id: int | None = Field(default=None, primary_key=True)
    status: RequisitionStatus
    submission_date: datetime
    approval_date: datetime | None = None
    delivery_date: datetime | None = None

class Items(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item_name: str
    brand: str | None = None
    model: str | None = None

class RequisitionItems(SQLModel, table=True):
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
    db_url = os.getenv("DATABASE_URL") or "sqlite:///./eoffice.db"
    engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False})
    with engine.connect() as connection:
            connection.execute(text("PRAGMA foreign_keys=ON"))
    
    return engine

def create_admin_user(engine):
    role = Roles(name='user_admin', description='Add, update, delete users and roles')
    with Session(engine) as session:
        try:
            session.add(role)
            session.commit()
            session.refresh(role)
            print('Role created successfully')
        except Exception as e:
            print(f"Error creating role: {e}")
            session.rollback()
            exit(1)

    if role.id is None:
        raise ValueError("Role ID is None. Cannot create RolePermissions without a valid role ID.")
    
    role_permissions = RolePermissions(role_id=role.id, permission=UserAction.MANAGE_USER)
    with Session(engine) as session:
        try:
            session.add(role_permissions)
            session.commit()
            session.refresh(role_permissions)
            print('Role permissions created successfully')
        except Exception as e:
            print(f"Error creating role permissions: {e}")
            session.rollback()
            exit(1)

    username = 'admin'
    password = 'admin'
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = Users(
        username=username,
        password=hashed_password.decode('utf-8'),
        first_name='Admin',
        last_name='User',
        email='admin@eoffice',
        is_active=True,
        role_id=role.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    with Session(engine) as session:
        try:
            session.add(user)
            session.commit()
            session.refresh(user)
            print('Admin user created successfully')
        except Exception as e:
            print(f"Error creating admin user: {e}")
            session.rollback()
            exit(1)
        return username, password

if __name__ == '__main__':
    engine = create_db_connection()
    
    try:
        SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)
        print('Tables created successfully')
    except Exception as e:
        print(f"Error creating tables: {e}")
        exit(1)

    try:
        create_admin_user(engine)
        print('Admin user created successfully')
    except Exception as e:
        print(f"Error creating admin user: {e}")
        exit(1)
    
        
