from sqlmodel import Session
from src.models import create_db_connection

def get_session():
    engine = create_db_connection()
    with Session(engine) as session:
        yield session