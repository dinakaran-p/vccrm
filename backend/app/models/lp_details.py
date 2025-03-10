from sqlalchemy import Column, String, Date, Numeric, Boolean, ForeignKey, Text, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database.base import Base
import uuid
from datetime import datetime

class LPDetails(Base):
    __tablename__ = "lp_details"

    lp_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lp_name = Column(String, nullable=False)
    mobile_no = Column(String(20))
    email = Column(String, nullable=False)
    address = Column(Text)
    nominee = Column(String)
    pan = Column(String(20))
    dob = Column(Date)
    doi = Column(Date, nullable=True)
    gender = Column(String(10))
    date_of_agreement = Column(Date)
    commitment_amount = Column(Numeric(15, 2))
    acknowledgement_of_ppm = Column(Boolean, default=False)
    dpid = Column(String(50))
    client_id = Column(String(50))
    cml = Column(String(50))
    isin = Column(String(50))
    class_of_shares = Column(String(20))
    citizenship = Column(String(50))
    type = Column(String(50))  # Individual, Corporate, etc.
    geography = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=datetime.now)

    # Relationships
    drawdowns = relationship("LPDrawdown", back_populates="lp")
    compliance_records = relationship("ComplianceRecord", back_populates="lp")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.lp_id:
            self.lp_id = uuid.uuid4()
