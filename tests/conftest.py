import pytest
import json
import os
from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from src.main import app
from src.models import create_db_connection, create_admin_user

@pytest.fixture(name="engine")
def engine_fixture(monkeypatch):
    # Override the DATABASE_URL to use the test database file
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./tests/test_eoffice.db")
    engine = create_db_connection()
    yield engine

@pytest.fixture(name="client")
def client_fixture(engine):
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as client:
        yield client

    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="admin_user")
def admin_user_fixture(engine):
    username, password = create_admin_user(engine)
    return {
        "username": username, 
        "password": password
    }

TOKEN_FILE = "test_token.json"
@pytest.fixture(autouse=True)
def auth_token(client, admin_user):
    """Get token via API and save to file"""
    login_data = {
        "username": admin_user["username"],
        "password": admin_user["password"]
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
def role_id(client, auth_headers):
    role_data = {
        "name": "default_role",
        "description": "Default role for testing"
    }
    response = client.post("/users/roles", json=role_data, headers=auth_headers)
    assert response.status_code == 200
    return response.json()["id"]

@pytest.fixture
def user_data(role_id):
    return {
        "username": "testuser",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
        "role_id": role_id  # now using role_id (an integer) as required by the new model
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
