from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskState(str, Enum):
    OPEN = "Open"
    PENDING = "Pending"
    REVIEW_REQUIRED = "Review Required"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"

class TaskCategory(str, Enum):
    SEBI = "SEBI"
    RBI = "RBI"
    IT_GST = "IT/GST"

class ComplianceTaskBase(BaseModel):
    description: str
    deadline: datetime
    category: TaskCategory
    assignee_id: UUID4
    reviewer_id: Optional[UUID4] = None
    approver_id: Optional[UUID4] = None
    recurrence: Optional[str] = None
    dependent_task_id: Optional[UUID4] = None

class ComplianceTaskCreate(ComplianceTaskBase):
    pass

class ComplianceTaskUpdate(BaseModel):
    state: Optional[TaskState] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    category: Optional[TaskCategory] = None
    assignee_id: Optional[UUID4] = None
    reviewer_id: Optional[UUID4] = None
    approver_id: Optional[UUID4] = None
    recurrence: Optional[str] = None
    dependent_task_id: Optional[UUID4] = None

class ComplianceTaskResponse(ComplianceTaskBase):
    compliance_task_id: UUID4
    state: TaskState
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
