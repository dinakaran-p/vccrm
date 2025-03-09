from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, create_engine, String, Boolean, DateTime, Text, select, Integer
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, EmailStr, ConfigDict
import jwt
import os
from werkzeug.utils import secure_filename
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import json
import csv
from io import StringIO
from enum import Enum
from datetime import date

# Configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
SQLALCHEMY_DATABASE_URI = "sqlite:///taskreminder.db"
UPLOAD_FOLDER = "uploads"

# Add these to your configuration section
GOOGLE_CLIENT_ID = "your-client-id"
GOOGLE_CLIENT_SECRET = "your-client-secret"
GOOGLE_REDIRECT_URI = "http://<devfrontend>/user"
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/calendar.events"
]

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# SQLAlchemy Models
class Base(DeclarativeBase):
    pass

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False}
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Models
class User(Base):
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    google_credentials: Mapped[Optional[str]] = mapped_column(Text)

    assigned_tasks = relationship(
        'Task',
        foreign_keys='Task.user_id',
        back_populates='assignee'
    )
    created_tasks = relationship(
        'Task',
        foreign_keys='Task.created_by',
        back_populates='creator'
    )

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        try:
            return pwd_context.verify(password, self.password_hash)
        except:
            return False

class Task(Base):
    __tablename__ = "task"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default='pending')
    file_path: Mapped[Optional[str]] = mapped_column(String(200))
    
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    assignee = relationship('User', foreign_keys=[user_id], back_populates='assigned_tasks')
    creator = relationship('User', foreign_keys=[created_by], back_populates='created_tasks')

# Add new enums and constants
class Frequency(str, Enum):
    ONE_TIME = "One Time"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"
    WHEN_REQUIRED = "When Required"

class DocumentType(str, Enum):
    TEXT_FIELD = "Text Field"
    DOCUMENT = "Document"

# Add new models
class ComplianceTask(Base):
    __tablename__ = "compliance_task"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    process_category: Mapped[str] = mapped_column(String(100))
    process_subcat: Mapped[str] = mapped_column(String(100))
    process_code: Mapped[str] = mapped_column(String(50), unique=True)
    predecessor: Mapped[Optional[str]] = mapped_column(String(50))
    due_date: Mapped[datetime] = mapped_column(DateTime)
    frequency: Mapped[str] = mapped_column(String(50))
    duration_days: Mapped[Optional[int]] = mapped_column(Integer)
    task_description: Mapped[str] = mapped_column(Text)
    inputs: Mapped[str] = mapped_column(Text)  # JSON string
    outputs: Mapped[str] = mapped_column(Text)  # JSON string
    method: Mapped[str] = mapped_column(String(50))
    owner: Mapped[str] = mapped_column(String(100))
    completion_flag: Mapped[str] = mapped_column(String(100))
    completion_feedback: Mapped[str] = mapped_column(String(200))
    document_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completion_data: Mapped[Optional[str]] = mapped_column(Text)  # Stores either file path or text content

# Pydantic Models
class LoginRequest(BaseModel):
    email: str
    password: str

class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(TaskBase):
    assigned_to: int

class TaskOut(TaskBase):
    id: int
    status: str
    file_path: Optional[str]
    created_at: datetime
    assignee: str
    creator: str

    @classmethod
    def from_task(cls, task: Task) -> "TaskOut":
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            status=task.status,
            file_path=task.file_path,
            created_at=task.created_at,
            assignee=task.assignee.username,
            creator=task.creator.username
        )

class GoogleAuthResponse(BaseModel):
    code: str

# Add Pydantic models
class ComplianceTaskCreate(BaseModel):
    process_category: str
    process_subcat: str
    process_code: str
    predecessor: Optional[str] = None
    due_date: datetime
    frequency: str
    duration_days: Optional[int] = None
    task_description: str
    inputs: List[str]
    outputs: List[str]
    method: str
    owner: str
    completion_flag: str
    completion_feedback: str
    document_type: str

class ComplianceTaskOut(ComplianceTaskCreate):
    id: int
    status: str
    completed_at: Optional[datetime] = None
    completion_data: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Database Session
def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

# Authentication
def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.post("/auth/login")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not user.verify_password(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "user_id": user.id,
        "is_admin": user.is_admin
    }

@app.post("/admin/users", response_model=UserOut)
async def create_user(user: UserCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_user = User(
        username=user.username,
        email=user.email,
        is_admin=user.is_admin
    )
    db_user.set_password(user.password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/admin/users", response_model=List[UserOut])
async def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(User).all()

@app.post("/tasks", response_model=TaskOut)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    assignee = db.query(User).filter(User.id == task.assigned_to).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assigned user not found")
    
    db_task = Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        user_id=task.assigned_to,
        created_by=current_user.id
    )
    
    # Create Google Calendar event if user has Google credentials
    if current_user.google_credentials:
        credentials = Credentials.from_authorized_user_info(
            json.loads(current_user.google_credentials)
        )
        calendar_service = build('calendar', 'v3', credentials=credentials)
        
        event = {
            'summary': task.title,
            'description': task.description,
            'start': {
                'dateTime': task.due_date.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (task.due_date + timedelta(hours=1)).isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        calendar_service.events().insert(calendarId='primary', body=event).execute()
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Explicitly load relationships
    db.refresh(db_task, attribute_names=['assignee', 'creator'])
    
    return TaskOut.from_task(db_task)

@app.get("/tasks", response_model=List[TaskOut])
async def get_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = select(Task).options(selectinload(Task.assignee), selectinload(Task.creator))
    
    if current_user.is_admin:
        tasks = db.execute(query).scalars().all()
    else:
        tasks = db.execute(query.where(Task.user_id == current_user.id)).scalars().all()
    
    return [TaskOut.from_task(task) for task in tasks]

@app.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if current_user.google_credentials:
        credentials = Credentials.from_authorized_user_info(
            json.loads(current_user.google_credentials)
        )
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Upload file to Google Drive
        file_metadata = {'name': f"{task_id}_{file.filename}"}
        media = MediaIoBaseUpload(
            BytesIO(await file.read()),
            mimetype=file.content_type,
            resumable=True
        )
        
        file_upload = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_path = f"https://drive.google.com/file/d/{file_upload['id']}/view"
    else:
        # Fallback to local storage
        filename = secure_filename(f"{task_id}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, "wb+") as file_object:
            content = await file.read()
            file_object.write(content)
        file_path = filename
    
    task.status = "completed"
    task.completed_at = datetime.utcnow()
    task.file_path = file_path
    
    db.commit()
    return {"message": "Task completed successfully"}

@app.get("/auth/google/login")
async def google_auth_url():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uri": GOOGLE_REDIRECT_URI,
            }
        },
        scopes=SCOPES
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
#return name and email and role and store the same way as the db is he login with credentials or using google sign in      

    return {"url": auth_url}

@app.post("/auth/google/callback")
async def google_auth_callback(
    response: GoogleAuthResponse,
    db: Session = Depends(get_db)
):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uri": GOOGLE_REDIRECT_URI,
            }
        },
        scopes=SCOPES
    )
    
    flow.fetch_token(code=response.code)
    credentials = flow.credentials
    
    # Get user info from Google
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    
    # Check if user exists
    user = db.query(User).filter(User.email == user_info['email']).first()
    if not user:
        user = User(
            username=user_info['email'].split('@')[0],
            email=user_info['email'],
            is_admin=False,
            google_credentials=credentials.to_json()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.google_credentials = credentials.to_json()
        db.commit()
    
    # Create access token
    access_token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "user_id": user.id,
        "is_admin": user.is_admin
    }

# Add new routes
@app.post("/compliance/upload-tasks")
async def upload_compliance_tasks(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    content = await file.read()
    csv_content = StringIO(content.decode())
    csv_reader = csv.DictReader(csv_content)
    
    tasks_created = []
    for row in csv_reader:
        # Skip header or empty rows
        if not row["ProcessCode"]:
            continue

        task = ComplianceTask(
            process_category=row["ProcessCategory"],
            process_subcat=row["ProcessSubcat"],
            process_code=row["ProcessCode"],
            predecessor=row["Predecessor"] or None,
            due_date=datetime.strptime(row["Date/Time"], "%d/%m/%Y"),
            frequency=row["Frequency"],
            duration_days=int(row["Duration (Days)"]) if row["Duration (Days)"] else None,
            task_description=row["Task"],
            inputs=json.dumps([row["Input1"], row["Input2"], row["Input3"]]),
            outputs=json.dumps([row["Output1"], row["Output2"], row["Output3"]]),
            method=row["Method"],
            owner=row["Owner"],
            completion_flag=row["CompletionFlag"],
            completion_feedback=row["CompletionFeedback"],
            document_type=row["Document type"]
        )
        db.add(task)
        tasks_created.append(task)
    
    db.commit()
    return {"message": f"Successfully created {len(tasks_created)} tasks"}

@app.post("/compliance/tasks/{task_id}/complete")
async def complete_compliance_task(
    task_id: int,
    completion_data: str = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if predecessor task is completed
    if task.predecessor:
        predecessor = db.query(ComplianceTask).filter(
            ComplianceTask.process_code == task.predecessor
        ).first()
        if predecessor and predecessor.status != "completed":
            raise HTTPException(
                status_code=400,
                detail="Predecessor task must be completed first"
            )

    if task.document_type == DocumentType.DOCUMENT and not file:
        raise HTTPException(
            status_code=400,
            detail="File upload required for document type tasks"
        )
    
    if task.document_type == DocumentType.TEXT_FIELD and not completion_data:
        raise HTTPException(
            status_code=400,
            detail="Completion text required for text field type tasks"
        )

    if file:
        # Store file with process code in filename
        filename = secure_filename(f"{task.process_code}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, "wb+") as file_object:
            content = await file.read()
            file_object.write(content)
        task.completion_data = filename
    else:
        task.completion_data = completion_data

    task.status = "completed"
    task.completed_at = datetime.utcnow()
    
    # Create next recurring task if applicable
    if task.frequency != Frequency.ONE_TIME:
        next_due_date = calculate_next_due_date(task.due_date, task.frequency)
        new_task = ComplianceTask(
            **{k: v for k, v in task.__dict__.items() if k not in ('id', 'status', 'completed_at', 'completion_data', 'due_date')}
        )
        new_task.due_date = next_due_date
        db.add(new_task)

    db.commit()
    return {"message": "Task completed successfully"}

def calculate_next_due_date(current_due_date: datetime, frequency: str) -> datetime:
    if frequency == Frequency.DAILY:
        return current_due_date + timedelta(days=1)
    elif frequency == Frequency.WEEKLY:
        return current_due_date + timedelta(weeks=1)
    elif frequency == Frequency.MONTHLY:
        return current_due_date + relativedelta(months=1)
    elif frequency == Frequency.QUARTERLY:
        return current_due_date + relativedelta(months=3)
    elif frequency == Frequency.YEARLY:
        return current_due_date + relativedelta(years=1)
    return current_due_date

@app.get("/compliance/tasks", response_model=List[ComplianceTaskOut])
async def get_compliance_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = select(ComplianceTask)
    if not current_user.is_admin:
        query = query.where(ComplianceTask.owner == current_user.username)
    
    tasks = db.execute(query).scalars().all()
    return tasks

# Initialize database and admin user
def init_db():
    Base.metadata.create_all(bind=engine)
    db = Session(engine)
    try:
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                username="admin",
                is_admin=True
            )
            admin.set_password("admin123")
            db.add(admin)
            db.commit()
    finally:
        db.close()

init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_fast:app", host="0.0.0.0", port=8000, reload=True)
