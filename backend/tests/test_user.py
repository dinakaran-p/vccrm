import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.models.user import User
import os

# Test database URL
DATABASE_URL = "postgresql://vccrm:vccrm@localhost:5432/vccrm_test"

@pytest.fixture(scope="function")
def test_db():
    # Create test database engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(engine)

def test_create_user(test_db):
    # Create a test user
    test_user = User(
        name="Test User",
        email="test@example.com",
        role="user",
        password_hash="hashed_password",
        mfa_enabled=False,
        phone="+1234567890"
    )
    
    # Add user to database
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)
    
    # Query the user
    db_user = test_db.query(User).filter(User.email == "test@example.com").first()
    
    # Verify user was created correctly
    assert db_user is not None
    assert db_user.name == "Test User"
    assert db_user.email == "test@example.com"
    assert db_user.role == "user"
    assert db_user.mfa_enabled == False
    assert db_user.phone == "+1234567890"
