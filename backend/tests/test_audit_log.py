import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database.base import Base, get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.compliance_task import ComplianceTask, TaskState, TaskCategory
from main import app as fastapi_app
import uuid
from datetime import datetime, timedelta
import jwt
from app.auth.security import SECRET_KEY, ALGORITHM
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

# Mock JWT token creation
def create_test_token(email: str, role: str):
    expire = datetime.utcnow() + timedelta(days=1)
    payload = {
        "sub": email,
        "role": role,
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@pytest.fixture(scope="function")
def setup_db():
    # Create all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Enable UUID extension for PostgreSQL
    db = TestingSessionLocal()
    db.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
    db.commit()
    db.close()
    
    yield
    
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_client(setup_db):
    fastapi_app.dependency_overrides[get_db] = override_get_db
    client = TestClient(fastapi_app)
    yield client
    fastapi_app.dependency_overrides.clear()

@pytest.fixture
def test_user(test_client):
    # Hash a known password
    password = "testpassword"
    hashed_password = get_password_hash(password)
    
    db = TestingSessionLocal()
    user_id = uuid.uuid4()
    user_data = {
        "user_id": user_id,
        "name": "Test User",
        "email": "test@example.com",
        "role": "Fund Manager",
        "password_hash": hashed_password
    }
    test_user = User(**user_data)
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    db.close()
    
    # Add the plaintext password to the user object for testing
    test_user.plain_password = password
    return test_user

@pytest.fixture
def test_token(test_user):
    return create_test_token(test_user.email, test_user.role)

def test_login_creates_audit_log(test_client, test_user):
    """Test that successful login creates an audit log entry"""
    # Clear any existing audit logs
    db = TestingSessionLocal()
    db.query(AuditLog).delete()
    db.commit()
    
    # Perform login
    response = test_client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": test_user.plain_password}
    )
    
    # Check successful login
    assert response.status_code == 200, f"Login failed with status {response.status_code}: {response.text}"
    
    # Check audit log
    audit_logs = db.query(AuditLog).filter(
        AuditLog.user_id == test_user.user_id,
        AuditLog.activity == "login"
    ).all()
    
    # Check that at least one audit log was created for the login attempt
    assert len(audit_logs) > 0, "No audit log entries found for login"
    db.close()

def test_reports_endpoint(test_client, test_user, test_token):
    """Test that the task stats reporting endpoint returns the correct data"""
    # Set up some tasks with different states
    db = TestingSessionLocal()
    
    # Create a completed task
    completed_task = ComplianceTask(
        compliance_task_id=uuid.uuid4(),
        description="Completed Task",
        deadline=datetime.utcnow() - timedelta(days=1),
        state=TaskState.COMPLETED.value,
        category=TaskCategory.SEBI.value,
        assignee_id=test_user.user_id  # Use the test user as assignee
    )
    
    # Create an open task
    open_task = ComplianceTask(
        compliance_task_id=uuid.uuid4(),
        description="Open Task",
        deadline=datetime.utcnow() + timedelta(days=1),
        state=TaskState.OPEN.value,
        category=TaskCategory.SEBI.value,
        assignee_id=test_user.user_id  # Use the test user as assignee
    )
    
    # Create an overdue task
    overdue_task = ComplianceTask(
        compliance_task_id=uuid.uuid4(),
        description="Overdue Task",
        deadline=datetime.utcnow() - timedelta(days=1),
        state=TaskState.OPEN.value,
        category=TaskCategory.SEBI.value,
        assignee_id=test_user.user_id  # Use the test user as assignee
    )
    
    db.add_all([completed_task, open_task, overdue_task])
    db.commit()
    
    # Test the reports endpoint
    headers = {"Authorization": f"Bearer {test_token}"}
    response = test_client.get("/api/reports/tasks-stats", headers=headers)
    
    # Check response
    assert response.status_code == 200, f"Error response: {response.text}"
    data = response.json()
    
    # There should be 3 total tasks
    assert data["total_tasks"] >= 3
    
    # There should be at least 1 completed task
    assert data["completed_tasks"] >= 1
    
    # There should be at least 1 overdue task
    assert data["overdue_tasks"] >= 1
    
    db.close()
