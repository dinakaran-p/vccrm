import pytest
import os
import shutil
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app.database.base import Base, get_db
from app.models.user import User
from app.models.document import Document, TaskDocument, DocumentStatus, DocumentCategory
from app.models.compliance_task import ComplianceTask
from main import app as fastapi_app
import uuid
import io
from app.schemas.document import DocumentCreate
from pathlib import Path
import jwt
from app.auth.security import SECRET_KEY, ALGORITHM

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
def test_client():
    # Create test uploads directory
    test_uploads_dir = Path("test_uploads")
    test_uploads_dir.mkdir(exist_ok=True)
    
    # Mock the upload directory path for testing
    import app.utils.file_storage
    original_upload_dir = app.utils.file_storage.UPLOAD_DIR
    app.utils.file_storage.UPLOAD_DIR = test_uploads_dir
    
    Base.metadata.create_all(bind=engine)
    fastapi_app.dependency_overrides[get_db] = override_get_db
    client = TestClient(fastapi_app)
    yield client
    
    # Clean up
    Base.metadata.drop_all(bind=engine)
    fastapi_app.dependency_overrides.clear()
    
    # Restore original upload dir
    app.utils.file_storage.UPLOAD_DIR = original_upload_dir
    
    # Remove test uploads directory
    if test_uploads_dir.exists():
        shutil.rmtree(test_uploads_dir)

@pytest.fixture
def test_user(test_client):
    db = TestingSessionLocal()
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "role": "Fund Manager",
        "password_hash": "hashed_password"  
    }
    test_user = User(**user_data)
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    db.close()
    return test_user

@pytest.fixture
def test_admin_user(test_client):
    db = TestingSessionLocal()
    user_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "role": "Admin",
        "password_hash": "hashed_password"  
    }
    admin_user = User(**user_data)
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    db.close()
    return admin_user

@pytest.fixture
def test_normal_user(test_client):
    db = TestingSessionLocal()
    user_data = {
        "name": "Normal User",
        "email": "normal@example.com",
        "role": "LP",
        "password_hash": "hashed_password"  
    }
    normal_user = User(**user_data)
    db.add(normal_user)
    db.commit()
    db.refresh(normal_user)
    db.close()
    return normal_user

@pytest.fixture
def test_token(test_user):
    return create_test_token(test_user.email, test_user.role)

@pytest.fixture
def admin_token(test_admin_user):
    return create_test_token(test_admin_user.email, test_admin_user.role)

@pytest.fixture
def normal_user_token(test_normal_user):
    return create_test_token(test_normal_user.email, test_normal_user.role)

@pytest.fixture
def test_document(test_client, test_token):
    """Create a test document for use in tests"""
    headers = {"Authorization": f"Bearer {test_token}"}
    file_content = b"Test file content"
    file = io.BytesIO(file_content)
    files = {"file": ("test_doc.txt", file, "text/plain")}
    data = {
        "name": "Test Document",
        "category": "KYC"
    }
    response = test_client.post("/api/documents/upload", headers=headers, files=files, data=data)
    return response.json()

@pytest.fixture
def test_compliance_task(test_client, test_user):
    """Create a test compliance task for use in tests"""
    db = TestingSessionLocal()
    task_data = {
        "description": "Test Description",
        "deadline": datetime.now() + timedelta(days=7),
        "state": "Open",
        "category": "SEBI",
        "assignee_id": test_user.user_id  
    }
    
    task = ComplianceTask(**task_data)
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.compliance_task_id
    db.close()
    return {"compliance_task_id": str(task_id)}

def test_upload_document_by_authorized_user(test_client, test_token):
    """Test that authorized users (Fund Manager, Compliance Officer, Admin) can upload documents"""
    headers = {"Authorization": f"Bearer {test_token}"}

    # Create test file content
    file_content = b"This is a test file content"
    file = io.BytesIO(file_content)

    # Prepare the multipart form data
    files = {"file": ("test_file.txt", file, "text/plain")}
    data = {
        "name": "Test Document",
        "category": "KYC"
    }

    response = test_client.post("/api/documents/upload", headers=headers, files=files, data=data)
    
    assert response.status_code == 201
    assert response.json()["name"] == "Test Document"
    assert response.json()["category"] == "KYC"
    assert response.json()["status"] == "Active"  

def test_upload_document_by_unauthorized_user(test_client, normal_user_token):
    """Test that unauthorized users (LP) cannot upload documents"""
    headers = {"Authorization": f"Bearer {normal_user_token}"}

    # Create test file content
    file_content = b"This is a test file content"
    file = io.BytesIO(file_content)

    # Prepare the multipart form data
    files = {"file": ("test_file.txt", file, "text/plain")}
    data = {
        "name": "Test Document",
        "category": "KYC"
    }

    response = test_client.post("/api/documents/upload", headers=headers, files=files, data=data)
    
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()

def test_list_documents_with_filters(test_client, admin_token, test_document):
    """Test listing documents with various filters"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test without filters
    response = test_client.get("/api/documents/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
    
    # Test with category filter
    response = test_client.get("/api/documents/?category=KYC", headers=headers)
    assert response.status_code == 200
    assert all(doc["category"] == "KYC" for doc in response.json())
    
    # Test with name filter
    response = test_client.get("/api/documents/?name=Test", headers=headers)
    assert response.status_code == 200
    assert all("Test" in doc["name"] for doc in response.json())
    
    # Test with status filter
    response = test_client.get("/api/documents/?status=Active", headers=headers)  
    assert response.status_code == 200
    assert all(doc["status"] == "Active" for doc in response.json())  

def test_link_document_to_task(test_client, test_token, test_document, test_compliance_task):
    """Test linking a document to a compliance task"""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    document_id = test_document["document_id"]
    task_id = test_compliance_task["compliance_task_id"]
    
    # We need to include both document_id and compliance_task_id in the payload
    # because the TaskDocumentCreate schema requires both
    payload = {
        "compliance_task_id": task_id,
        "document_id": document_id
    }
    
    response = test_client.post(f"/api/documents/{document_id}/link-to-task", 
                                headers=headers, 
                                json=payload)
    
    assert response.status_code == 200
    assert response.json()["document_id"] == document_id
    assert response.json()["compliance_task_id"] == task_id
    
    # Test linking the same document again (should fail)
    response = test_client.post(f"/api/documents/{document_id}/link-to-task", 
                                headers=headers, 
                                json=payload)
    
    assert response.status_code == 400
    assert "already linked" in response.json()["detail"].lower()

def test_delete_document(test_client, admin_token, test_document):
    """Test that admin users can delete documents"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    document_id = test_document["document_id"]
    
    # First check it exists
    response = test_client.get(f"/api/documents/{document_id}", headers=headers)
    assert response.status_code == 200
    
    # Delete it
    response = test_client.delete(f"/api/documents/{document_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify it's gone
    response = test_client.get(f"/api/documents/{document_id}", headers=headers)
    assert response.status_code == 404
