from fastapi import FastAPI, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.models.user import User
from app.models.compliance_task import ComplianceTask, TaskState, TaskCategory
from app.auth.security import get_password_hash, verify_password, create_access_token, get_current_user, check_role
from app.schemas.compliance_task import ComplianceTaskCreate, ComplianceTaskUpdate, ComplianceTaskResponse
from app.api.documents import router as documents_router
from app.api.reports import router as reports_router
from app.api.lp import router as lp_router
from app.api.compliance import router as compliance_router
from app.utils.audit import log_activity
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uuid
from datetime import timedelta, datetime
from sqlalchemy.exc import IntegrityError
import traceback
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import os

app = FastAPI()

# Mount the routers
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
app.include_router(lp_router, prefix="/api/lps", tags=["lps"])
app.include_router(compliance_router, prefix="/api/compliance", tags=["compliance"])

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str
    password: str
    mfa_enabled: bool = False
    phone: Optional[str] = None

class UserResponse(BaseModel):
    user_id: uuid.UUID
    name: str
    email: str
    role: str
    mfa_enabled: bool
    phone: Optional[str]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user with this email already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash the password before storing
        hashed_password = get_password_hash(user.password)
        
        # Validate role
        valid_roles = ["Fund Manager", "Compliance Officer", "LP"]
        if user.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )

        db_user = User(
            name=user.name,
            email=user.email,
            role=user.role,
            password_hash=hashed_password,
            mfa_enabled=user.mfa_enabled,
            phone=user.phone
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e)}"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        error_details = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unexpected error: {str(e)}\nDetails: {error_details}"
        )

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log successful login
    log_activity(db, "login", user.user_id, f"User {user.email} logged in")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user["sub"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/fund-manager/dashboard")
async def fund_manager_dashboard(current_user: dict = Depends(check_role("Fund Manager"))):
    return {
        "message": "Welcome to Fund Manager Dashboard",
        "user": current_user["sub"]
    }

# Compliance Tasks Endpoints

@app.post("/api/tasks/", response_model=ComplianceTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: ComplianceTaskCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Validate assignee exists
        assignee = db.query(User).filter(User.user_id == task.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")

        # Validate dependent task if specified
        if task.dependent_task_id:
            dependent_task = db.query(ComplianceTask).filter(
                ComplianceTask.compliance_task_id == task.dependent_task_id
            ).first()
            if not dependent_task:
                raise HTTPException(status_code=404, detail="Dependent task not found")

        db_task = ComplianceTask(**task.model_dump())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        # Log task creation
        user_id = None
        if "sub" in current_user:
            user = db.query(User).filter(User.email == current_user["sub"]).first()
            if user:
                user_id = user.user_id
                
        log_activity(
            db, 
            "task_created", 
            user_id, 
            f"Task created: {db_task.compliance_task_id} - {task.description}"
        )
        
        return db_task

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tasks/", response_model=List[ComplianceTaskResponse])
async def get_tasks(
    state: Optional[TaskState] = None,
    category: Optional[TaskCategory] = None,
    assignee_id: Optional[uuid.UUID] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ComplianceTask)
    
    if state:
        query = query.filter(ComplianceTask.state == state)
    if category:
        query = query.filter(ComplianceTask.category == category)
    if assignee_id:
        query = query.filter(ComplianceTask.assignee_id == assignee_id)

    return query.all()

@app.patch("/api/tasks/{task_id}", response_model=ComplianceTaskResponse)
async def update_task(
    task_id: uuid.UUID,
    task_update: ComplianceTaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = db.query(ComplianceTask).filter(ComplianceTask.compliance_task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if trying to complete a task with incomplete dependency
    if (task_update.state == TaskState.COMPLETED and db_task.dependent_task_id):
        dependent_task = db.query(ComplianceTask).filter(
            ComplianceTask.compliance_task_id == db_task.dependent_task_id
        ).first()
        if dependent_task and dependent_task.state != TaskState.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail="Cannot complete task: dependent task is not completed"
            )

    # Update task fields
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    try:
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
