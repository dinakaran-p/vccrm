import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base


class AuditLog(Base):
    """
    Model for storing audit logs related to user activities in the system.
    Tracks actions taken by users for compliance and accountability purposes.
    """
    __tablename__ = "audit_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    activity = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    details = Column(Text, nullable=True)

    # Relationship with User model
    user = relationship("User", back_populates="audit_logs")
