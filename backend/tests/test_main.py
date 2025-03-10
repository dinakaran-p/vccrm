from fastapi.testclient import TestClient
from main import app
from app.database.base import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

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

def test_read_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_user(test_client):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "role": "user",
        "password": "testpassword",
        "mfa_enabled": False,
        "phone": "+1234567890"
    }
    
    response = test_client.post("/users/", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]
    assert data["mfa_enabled"] == user_data["mfa_enabled"]
    assert data["phone"] == user_data["phone"]
    assert "user_id" in data
