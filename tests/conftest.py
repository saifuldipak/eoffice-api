import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from src.main import app
from src.dependency import get_session

# Create a test database engine
test_engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})

# Override the get_session dependency to use the test database
def override_get_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(name="client")
def client_fixture():
    SQLModel.metadata.create_all(test_engine)
    with TestClient(app) as client:
        yield client
    SQLModel.metadata.drop_all(test_engine)

import pytest

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