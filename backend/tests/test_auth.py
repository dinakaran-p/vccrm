import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base, get_db
from app.models.user import User
from main import app
import jwt
from datetime import datetime, timedelta
from app.auth.security import get_password_hash

# Test database URL
DATABASE_URL = "postgresql://vccrm:vccrm@localhost:5432/vccrm_test"

# Create test database engine
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def test_client():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    client = TestClient(app)
    
    yield client
    
    # Clean up
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(test_client):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "role": "Fund Manager",
        "password": "testpassword",
        "mfa_enabled": False,
        "phone": "+1234567890"
    }
    response = test_client.post("/users/", json=user_data)
    return response.json()

@pytest.fixture
def test_compliance_user(test_client):
    user_data = {
        "name": "Compliance User",
        "email": "compliance@example.com",
        "role": "Compliance Officer",
        "password": "testpassword",
        "mfa_enabled": False,
        "phone": "+1234567890"
    }
    response = test_client.post("/users/", json=user_data)
    return response.json()

def test_login_success(test_client, test_user):
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    response = test_client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(test_client, test_user):
    login_data = {
        "username": "test@example.com",
        "password": "wrongpassword"
    }
    response = test_client.post("/api/auth/login", data=login_data)
    assert response.status_code == 401

def test_get_current_user_without_token(test_client):
    response = test_client.get("/api/users/me")
    assert response.status_code == 401

def test_get_current_user_with_token(test_client, test_user):
    # First login to get the token
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    login_response = test_client.post("/api/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Use token to get current user info
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]

def test_fund_manager_only_endpoint_with_correct_role(test_client, test_user):
    # Login as Fund Manager
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    login_response = test_client.post("/api/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/api/fund-manager/dashboard", headers=headers)
    assert response.status_code == 200

def test_fund_manager_only_endpoint_with_wrong_role(test_client, test_compliance_user):
    # Login as Compliance Officer
    login_data = {
        "username": "compliance@example.com",
        "password": "testpassword"
    }
    login_response = test_client.post("/api/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Try to access Fund Manager only endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/api/fund-manager/dashboard", headers=headers)
    assert response.status_code == 403
