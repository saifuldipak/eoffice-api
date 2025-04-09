from sqlmodel import Session, select
from src.models import Users
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def create_user_in_db(session: Session, user_data):
    hashed_password = user_data.password
    db_user = Users(
        username=user_data.username,
        password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        role=user_data.role,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError:
        session.rollback()
        raise

def get_users_from_db(session: Session, username: str):
    statement = select(Users).where(Users.username.like(f"{username}%"))
    return session.exec(statement).all()

def delete_user_from_db(session: Session, username: str):
    statement = select(Users).where(Users.username == username)
    db_user = session.exec(statement).first()
    if db_user:
        session.delete(db_user)
        session.commit()
    return db_user

def update_user_in_db(session: Session, username: str, updated_data: dict):
    """
    Update user details based on the provided username and updated data.

    Args:
        session (Session): The database session.
        username (str): The username of the user to update.
        updated_data (dict): A dictionary containing the fields to update.

    Returns:
        Users: The updated user object, or None if the user does not exist.
    """
    statement = select(Users).where(Users.username == username)
    db_user = session.exec(statement).first()
    if not db_user:
        return None

    for key, value in updated_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    db_user.updated_at = datetime.now()

    try:
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError:
        session.rollback()
        raise