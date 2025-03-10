from sqlalchemy import Column, String, Date, Numeric, ForeignKey, Text, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database.base import Base
import uuid
from datetime import datetime

class LPDrawdown(Base):
    __tablename__ = "lp_drawdowns"

    drawdown_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lp_id = Column(UUID(as_uuid=True), ForeignKey("lp_details.lp_id"), nullable=False)
    drawdown_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    drawdown_percentage = Column(Numeric(5, 2))  # Percentage of total commitment
    payment_due_date = Column(Date, nullable=False)
    payment_received_date = Column(Date, nullable=True)
    payment_status = Column(String(50), nullable=False, default="Pending")  # Pending, Received, Overdue
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=datetime.now)

    # Relationships
    lp = relationship("LPDetails", back_populates="drawdowns")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.drawdown_id:
            self.drawdown_id = uuid.uuid4()
