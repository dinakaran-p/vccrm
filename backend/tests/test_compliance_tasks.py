import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app.database.base import Base, get_db
from app.models.user import User
from app.models.compliance_task import ComplianceTask, TaskState, TaskCategory
from main import app
import uuid

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
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(test_client):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "role": "Fund Manager",
        "password": "testpassword",
        "mfa_enabled": False
    }
    response = test_client.post("/users/", json=user_data)
    return response.json()

@pytest.fixture
def test_token(test_client, test_user):
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    response = test_client.post("/api/auth/login", data=login_data)
    return response.json()["access_token"]

def test_create_task(test_client, test_token, test_user):
    headers = {"Authorization": f"Bearer {test_token}"}
    task_data = {
        "description": "File quarterly SEBI report",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "category": "SEBI",
        "assignee_id": test_user["user_id"]
    }
    response = test_client.post("/api/tasks/", json=task_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == task_data["description"]
    assert data["state"] == "Open"

def test_get_tasks_with_filters(test_client, test_token, test_user):
    # Create test tasks
    headers = {"Authorization": f"Bearer {test_token}"}
    task_data = {
        "description": "File quarterly SEBI report",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "category": "SEBI",
        "assignee_id": test_user["user_id"]
    }
    test_client.post("/api/tasks/", json=task_data, headers=headers)
    
    # Test filtering by category
    response = test_client.get("/api/tasks/?category=SEBI", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "SEBI"

    # Test filtering by state
    response = test_client.get("/api/tasks/?state=Open", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["state"] == "Open"

def test_update_task_state(test_client, test_token, test_user):
    # Create a task
    headers = {"Authorization": f"Bearer {test_token}"}
    task_data = {
        "description": "File quarterly SEBI report",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "category": "SEBI",
        "assignee_id": test_user["user_id"]
    }
    create_response = test_client.post("/api/tasks/", json=task_data, headers=headers)
    task_id = create_response.json()["compliance_task_id"]
    
    # Update task state
    update_data = {"state": "Completed"}
    response = test_client.patch(f"/api/tasks/{task_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["state"] == "Completed"

def test_dependent_task_completion(test_client, test_token, test_user):
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # Create parent task
    parent_task_data = {
        "description": "Parent task",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "category": "SEBI",
        "assignee_id": test_user["user_id"]
    }
    parent_response = test_client.post("/api/tasks/", json=parent_task_data, headers=headers)
    parent_id = parent_response.json()["compliance_task_id"]
    
    # Create dependent task
    dependent_task_data = {
        "description": "Dependent task",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "category": "SEBI",
        "assignee_id": test_user["user_id"],
        "dependent_task_id": parent_id
    }
    dependent_response = test_client.post("/api/tasks/", json=dependent_task_data, headers=headers)
    dependent_id = dependent_response.json()["compliance_task_id"]
    
    # Try to complete dependent task before parent task
    update_data = {"state": "Completed"}
    response = test_client.patch(f"/api/tasks/{dependent_id}", json=update_data, headers=headers)
    assert response.status_code == 400
    assert "dependent task" in response.json()["detail"].lower()
