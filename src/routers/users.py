from fastapi import HTTPException, Depends, APIRouter
from typing import List
import logging
from sqlmodel import Session, select
from src.dependency import get_session
from src.auth import check_manage_user_permission
from src.db_queries import (
    create_user_in_db, get_users_from_db, delete_user_from_db, update_user_in_db,
    create_role_in_db, get_all_roles, update_role_in_db, delete_role_from_db,
    create_role_permission_in_db, delete_role_permission_from_db, get_all_role_permissions, get_role_permissions_by_role,
    create_team_in_db, get_team_by_name_from_db, update_team_in_db, delete_team_from_db, get_team_list_from_db
)
from src.models import UserCreate, UserInfo, UserUpdate, RoleCreate, RoleInfo, Roles, RolePermissions, RolePermissionCreate, TeamCreate, TeamInfo, TeamUpdate, Teams
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
    dependencies=[Depends(check_manage_user_permission)]
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
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    try:
        db_user = update_user_in_db(session, username, update_data)  # Use the update_user_in_db function
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Update failed due to integrity constraints (e.g., duplicate username or email)")
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# --- Team CRUD endpoints added in users.py ---
@router.post("/teams/", response_model=TeamInfo)
async def create_team(team: TeamCreate, session: Session = Depends(get_session)):
    new_team = Teams(**team.model_dump())
    try:
        created_team = create_team_in_db(session, new_team)
        return created_team
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Team with this name or description already exists")

@router.get("/teams/{team_name}", response_model=TeamInfo)
async def get_team(team_name: str, session: Session = Depends(get_session)):
    team = get_team_by_name_from_db(session, team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.get("/teams/", response_model=List[TeamInfo])
async def list_teams(session: Session = Depends(get_session)):
    teams = get_team_list_from_db(session)
    return teams

@router.patch("/teams/{team_name}", response_model=TeamInfo)
async def update_team(team_update_data: TeamUpdate, session: Session = Depends(get_session)):
    db_team = get_team_by_name_from_db(session, team_update_data.name)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found") 

    if db_team.description == team_update_data.description:
        raise HTTPException(status_code=400, detail="No changes detected in team description") 
    
    try:
        updated_team = update_team_in_db(session, team_update_data)
        return updated_team
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/teams/{team_name}")
async def delete_team(team_name: str, session: Session = Depends(get_session)):
    team = delete_team_from_db(session, team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"message": f"Team {team.name} successfully deleted"}

# CRUD endpoints for Roles
@router.post("/roles", response_model=RoleInfo)
async def create_role(role: RoleCreate, session: Session = Depends(get_session)):
    try:
        db_role = create_role_in_db(session, role)
        return db_role
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/roles/all", response_model=list[RoleInfo])
async def read_roles(session: Session = Depends(get_session)):
    roles = get_all_roles(session)
    return roles

@router.get("/roles/{role_id}", response_model=RoleInfo)
async def read_role(role_id: int, session: Session = Depends(get_session)):
    role = session.get(Roles, role_id)
    if not role:
         raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.patch("/roles/{role_id}", response_model=RoleInfo)
async def update_role(role_id: int, role_update: RoleCreate, session: Session = Depends(get_session)):
    update_data = role_update.model_dump(exclude_unset=True)
    try:
         role = update_role_in_db(session, role_id, update_data)
         if not role:
              raise HTTPException(status_code=404, detail="Role not found")
         return role
    except Exception as e:
         raise HTTPException(status_code=400, detail=str(e))

@router.delete("/roles/{role_id}")
async def delete_role(role_id: int, session: Session = Depends(get_session)):
    try:
        return_message = delete_role_from_db(session, role_id)
        return {"message": return_message}
    except ValueError:
        raise HTTPException(status_code=404, detail="Role not found")
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Role cannot be deleted, it used in RolePermission.Delete the RolePermission first")
    except Exception as e:
        logger.error(f"Error deleting role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# CRUD endpoints for RolePermissions
@router.post("/roles/permissions/", response_model=RolePermissions)
async def add_role_permission(
    role_permission: RolePermissionCreate, session: Session = Depends(get_session)
):
    try:
        rp = create_role_permission_in_db(session, role_permission)
        return rp
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/roles/permissions/", response_model=dict)
async def remove_role_permission(role_id: int, permission: str, session: Session = Depends(get_session)
):
    try:
        delete_role_permission_from_db(session, role_id, permission)
        return {
            "message": f"Role permission {permission} for Role ID {role_id} successfully deleted"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roles/permissions/", response_model=list[RolePermissions])
async def list_all_role_permissions(session: Session = Depends(get_session)):
    permissions = get_all_role_permissions(session)
    if not permissions:
        raise HTTPException(status_code=404, detail="No role permissions found")
    return permissions

@router.get("/roles/permissions/by-name/{role_name}", response_model=list[RolePermissions])
async def list_role_permissions_by_role_name(role_name: str, session: Session = Depends(get_session)):
    stmt = select(Roles).where(Roles.name == role_name)
    role = session.exec(stmt).first()
    if not role or role.id is None:
        raise HTTPException(status_code=404, detail=f"Role with name {role_name} not found")
    
    permissions = get_role_permissions_by_role(session, role.id)
    if not permissions:
        raise HTTPException(status_code=404, detail=f"No permissions found for role {role_name}")
    return permissions
