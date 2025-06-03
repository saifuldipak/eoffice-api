import pytest
import json
import os
from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from src.main import app
from src.models import create_db_connection, create_user, UserCreate, RequisitionUnit

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

@pytest.fixture
def user_data():
    return {
        "username": "test",
        "password": "test123",
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
    }


def add_user(engine, role_permission, user_data) -> tuple[str, str]:
    user = UserCreate(
        username=user_data["username"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        email=user_data["email"]
    )
    username, password = create_user(engine, "test_role", role_permission, user)
    return username, password

def get_auth_token(client, username, password, token_file):
    login_data = {
        "username": username,
        "password": password
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    token_data = response.json()

    # Save token to file
    with open(token_file, "w") as f:
        json.dump(token_data, f)

    return token_data["access_token"]
    
    
TOKEN_FILE = "auth_token.json"
@pytest.fixture
def auth_headers(engine, client, user_data, token_file=TOKEN_FILE):
    def _auth_headers(role_permission):
        username, password = add_user(engine, role_permission, user_data)
        token_data = get_auth_token(client, username, password, token_file)
        try:
            with open(token_file, "r") as f:
                token_data = json.load(f)
                return {"Authorization": f"Bearer {token_data['access_token']}"}
        except FileNotFoundError:
            pytest.fail("Token file not found. Make sure to run tests that generate the token first.")
    return _auth_headers

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

@pytest.fixture
def item_data():
    return {
        "type": 1,
        "brand": 1,
        "model": "Model X"
    }

@pytest.fixture
def created_item_type(client):
    def _create_item_type(headers, item_type_data):
        data = {"item_type": item_type_data}
        response = client.post("/requisitions/items/types/", json=data, headers=headers)
        assert response.status_code == 200
        return response.json()["id"]
    return _create_item_type

@pytest.fixture
def created_item_brand(client):
    def _create_item_brand(headers, item_brand_data):
        data = {"brand": item_brand_data}
        response = client.post("/requisitions/items/brands/", json=data, headers=headers)
        assert response.status_code == 200
        return response.json()["id"]
    return _create_item_brand

@pytest.fixture
def created_item(client):
    def _create_item(headers, type_id, brand_id, model):
        data = {
            "type": type_id,
            "brand": brand_id,
            "model": model
        }
        response = client.post("/requisitions/items/", json=data, headers=headers)
        assert response.status_code == 200
        return response.json()["id"]
    
    return _create_item

@pytest.fixture
def requisition_data():
    return {
        "item_id": 1,  # This should be replaced with a valid item ID
        "unit": RequisitionUnit.PIECE,
        "quantity": 10,
        "remark": "Test requisition"
    }
