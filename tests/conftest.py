import pytest
import json
import os
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from src.main import app
from src.dependency import get_session
from src.models import Users
from datetime import datetime
from src.auth import get_password_hash

# Create a test database engine
test_engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})

# Override the get_session dependency to use the test database
def override_get_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

TOKEN_FILE = "test_token.json"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "adminpassword"
ROLE = "user_admin"
FIRST_NAME = "Admin"
LAST_NAME = "User"
ADMIN_EMAIL = "admin@example.com"

def create_admin_user():
    """Create an admin user in the database directly"""
    session = next(override_get_session())
    admin = Users(
        username=ADMIN_USER,
        password=get_password_hash(ADMIN_PASSWORD),
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        email=ADMIN_EMAIL,
        role=ROLE,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin

@pytest.fixture(name="client")
def client_fixture():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    create_admin_user()
    with TestClient(app) as client:
        yield client
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(autouse=True)
def auth_token(client):
    """Get token via API and save to file"""
    login_data = {
        "username": f"{ADMIN_USER}",
        "password": f"{ADMIN_PASSWORD}"
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    
    # Save token to file
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)
    
    return token_data["access_token"]

@pytest.fixture
def auth_headers():
    """Read token from file and create headers"""
    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
            return {"Authorization": f"Bearer {token_data['access_token']}"}
    except FileNotFoundError:
        pytest.fail("Token file not found. Make sure to run tests that generate the token first.")

@pytest.fixture(autouse=True)
def cleanup():
    #Cleanup the token file after tests
    yield
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
        "role": "user_admin"
    }

@pytest.fixture
def group_data():
    return {
        "name": "testgroup",
        "description": "A test group"
    }

@pytest.fixture
def access_type_data():
    return {
        "type": "Read",
        "description": "Read access"
    }
