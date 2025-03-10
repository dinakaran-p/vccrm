from sqlalchemy import Column, String, DateTime, ForeignKey, text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base
import uuid
from datetime import datetime
import enum

class DocumentStatus(str, enum.Enum):
    ACTIVE = "Active"
    PENDING_APPROVAL = "Pending Approval"
    EXPIRED = "Expired"

class DocumentCategory(str, enum.Enum):
    CONTRIBUTION_AGREEMENT = "Contribution Agreement"
    KYC = "KYC"
    NOTIFICATION = "Notification"
    REPORT = "Report"
    OTHER = "Other"

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    date_uploaded = Column(DateTime(timezone=True), server_default=text('now()'))
    status = Column(String, nullable=False, server_default=DocumentStatus.ACTIVE.value)
    expiry_date = Column(Date, nullable=True)
    process_id = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=datetime.now)

    # Task documents relationship
    tasks = relationship("TaskDocument", back_populates="document")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.document_id:
            self.document_id = uuid.uuid4()

class TaskDocument(Base):
    __tablename__ = "task_documents"

    task_document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compliance_task_id = Column(UUID(as_uuid=True), ForeignKey('compliance_tasks.compliance_task_id'), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.document_id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))

    # Relationships
    document = relationship("Document", back_populates="tasks")
    task = relationship("ComplianceTask", backref="documents")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.task_document_id:
            self.task_document_id = uuid.uuid4()
