from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from src.auth import login_for_access_token
from src.dependency import get_session

router = APIRouter()

@router.post("/auth/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    return await login_for_access_token(form_data, session)