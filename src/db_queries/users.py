from sqlmodel import Session, select
from src.models import Users, Teams, TeamUpdate, UserCreate, RoleCreate, Roles, RolePermissions, RolePermissionCreate
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from passlib.context import CryptContext

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
    statement = select(Users).where(Users.username.ilike(f"{username}%")) # type: ignore
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

def create_role_in_db(session: Session, role_data: RoleCreate) -> Roles:
    role = Roles(name=role_data.name, description=role_data.description)
    session.add(role)
    try:
        session.commit()
        session.refresh(role)
        return role
    except IntegrityError:
        session.rollback()
        raise
    except Exception:
        session.rollback()
        raise

def get_role_by_name_from_db(session: Session, name: str) -> Roles | None:
    statement = select(Roles).where(Roles.name == name)
    return session.exec(statement).first()

def get_all_roles(session: Session) -> list[Roles] | None:
    statement = select(Roles)
    return list(session.exec(statement).all())

def update_role_in_db(session: Session, role_id: int, update_data: dict) -> Roles | None:
    role = session.get(Roles, role_id)
    if not role:
        raise ValueError(f"Role with ID {role_id} not found")
 
    for key, value in update_data.items():
         if hasattr(role, key):
             setattr(role, key, value)
    
    try:
         session.commit()
         session.refresh(role)
         return role
    except IntegrityError:
         session.rollback()
         raise
    except Exception:
         session.rollback()
         raise

def delete_role_from_db(session: Session, role_id: int) -> str:
    role = session.get(Roles, role_id)
    if not role:
        raise ValueError(f"Role with ID {role_id} not found")
    
    try:
        session.delete(role)
        session.commit()
        return f"Role with ID {role_id} deleted successfully"
    except IntegrityError:
        session.rollback()
        raise
    except Exception:
        session.rollback()
        raise

def create_role_permission_in_db(session: Session, role_permission_data: RolePermissionCreate) -> RolePermissions:
    # Verify the role exists
    role = session.get(Roles, role_permission_data.role_id)
    if not role:
        raise ValueError(f"Role with ID {role_permission_data.role_id} not found")

    # Check for duplicate permission entry
    stmt = select(RolePermissions).where(
        RolePermissions.role_id == role_permission_data.role_id,
        RolePermissions.permission == role_permission_data.permission
    )
    existing_permission = session.exec(stmt).first()
    if existing_permission:
        raise ValueError(
            f"Role permission with Role ID {role_permission_data.role_id} and Permission {role_permission_data.permission} already exists"
        )

    role_permission_db = RolePermissions(**role_permission_data.model_dump())
    session.add(role_permission_db)
    try:
        session.commit()
        session.refresh(role_permission_db)
        return role_permission_db
    except Exception:
        session.rollback()
        raise

def delete_role_permission_from_db(session: Session, role_id: int, permission: str) -> None:
    stmt = select(RolePermissions).where(
        RolePermissions.role_id == role_id,
        RolePermissions.permission == permission
    )
    role_permission_in_db = session.exec(stmt).first()
    if not role_permission_in_db:
        raise ValueError(
            f"Role permission {permission} for Role ID {role_id} not found"
        )
    try:
        session.delete(role_permission_in_db)
        session.commit()
    except Exception:
        session.rollback()
        raise

def get_all_role_permissions(session: Session) -> list[RolePermissions]:
    stmt = select(RolePermissions)
    return list(session.exec(stmt).all())  # Explicitly convert to list

def get_role_permissions_by_role(session: Session, role_id: int) -> list[RolePermissions]:
    stmt = select(RolePermissions).where(RolePermissions.role_id == role_id)
    return list(session.exec(stmt).all())  # Explicitly convert to list
