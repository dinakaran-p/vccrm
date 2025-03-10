from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class DocumentStatus(str, Enum):
    ACTIVE = "Active"
    PENDING_APPROVAL = "Pending Approval"
    EXPIRED = "Expired"

class DocumentCategory(str, Enum):
    CONTRIBUTION_AGREEMENT = "Contribution Agreement"
    KYC = "KYC"
    NOTIFICATION = "Notification"
    REPORT = "Report"
    OTHER = "Other"

class DocumentBase(BaseModel):
    name: str
    category: DocumentCategory
    status: Optional[DocumentStatus] = DocumentStatus.ACTIVE
    expiry_date: Optional[date] = None
    process_id: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[DocumentCategory] = None
    status: Optional[DocumentStatus] = None
    expiry_date: Optional[date] = None
    process_id: Optional[str] = None

class DocumentInDB(DocumentBase):
    document_id: UUID4
    file_path: str
    date_uploaded: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Document(DocumentInDB):
    pass

class TaskDocumentCreate(BaseModel):
    compliance_task_id: UUID4
    document_id: UUID4

class TaskDocumentInDB(TaskDocumentCreate):
    task_document_id: UUID4
    created_at: datetime

    class Config:
        orm_mode = True

class TaskDocument(TaskDocumentInDB):
    pass

class DocumentWithTasks(Document):
    tasks: List[TaskDocumentInDB] = []
