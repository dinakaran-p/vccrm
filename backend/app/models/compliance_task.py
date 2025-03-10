from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database.base import Base
import uuid
from datetime import datetime
import enum

class TaskState(str, enum.Enum):
    OPEN = "Open"
    PENDING = "Pending"
    REVIEW_REQUIRED = "Review Required"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"

class TaskCategory(str, enum.Enum):
    SEBI = "SEBI"
    RBI = "RBI"
    IT_GST = "IT/GST"

class ComplianceTask(Base):
    __tablename__ = "compliance_tasks"

    compliance_task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String, nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=False)
    recurrence = Column(String, nullable=True)
    dependent_task_id = Column(UUID(as_uuid=True), ForeignKey('compliance_tasks.compliance_task_id'), nullable=True)
    state = Column(String, nullable=False, server_default=TaskState.OPEN.value)
    category = Column(String, nullable=False)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    approver_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=datetime.now)

    # Relationships
    assignee = relationship("User", foreign_keys=[assignee_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    approver = relationship("User", foreign_keys=[approver_id])
    dependent_task = relationship("ComplianceTask", remote_side=[compliance_task_id])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.compliance_task_id:
            self.compliance_task_id = uuid.uuid4()

    @property
    def task_state(self) -> TaskState:
        return TaskState(self.state)

    @task_state.setter
    def task_state(self, value: TaskState):
        self.state = value.value

    @property
    def task_category(self) -> TaskCategory:
        return TaskCategory(self.category)

    @task_category.setter
    def task_category(self, value: TaskCategory):
        self.category = value.value
