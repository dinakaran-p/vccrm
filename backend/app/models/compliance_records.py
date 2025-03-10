from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database.base import Base
import uuid
from datetime import datetime
from sqlalchemy import text

class FundComplianceRecord(Base):
    __tablename__ = "fund_compliance_records"
    
    record_id = Column(Integer, primary_key=True)
    entity_type = Column(String(50), default="Fund")
    compliance_status = Column(String(50), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=text('now()'))
    comments = Column(Text, nullable=True)

class LPComplianceRecord(Base):
    __tablename__ = "lp_compliance_records"
    
    record_id = Column(Integer, primary_key=True)
    entity_type = Column(String(50), default="LP")
    compliance_status = Column(String(50), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=text('now()'))
    comments = Column(Text, nullable=True)

class PortfolioComplianceRecord(Base):
    __tablename__ = "portfolio_compliance_records"
    
    record_id = Column(Integer, primary_key=True)
    entity_type = Column(String(50), default="Portfolio")
    compliance_status = Column(String(50), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=text('now()'))
    comments = Column(Text, nullable=True)


from sqlalchemy import Column, String, ForeignKey, Text, DateTime, text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database.base import Base
import uuid
from datetime import datetime
import enum

class ComplianceStatus(str, enum.Enum):
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    PENDING_REVIEW = "Pending Review"
    EXEMPTED = "Exempted"

class EntityType(str, enum.Enum):
    FUND = "Fund"
    LP = "LP"
    PORTFOLIO = "Portfolio"

class ComplianceRecord(Base):
    __tablename__ = "compliance_records"

    record_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, nullable=False)
    
    # Foreign keys for different entity types
    lp_id = Column(UUID(as_uuid=True), ForeignKey("lp_details.lp_id"), nullable=True)
    # Add other entity foreign keys as needed (e.g., fund_id, portfolio_id)
    
    compliance_type = Column(String, nullable=False)  # KYC, AML, Tax, etc.
    compliance_status = Column(String, nullable=False, default=ComplianceStatus.PENDING_REVIEW.value)
    due_date = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=text('now()'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=datetime.now)

    # Relationships
    lp = relationship("LPDetails", back_populates="compliance_records")
    user = relationship("User")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.record_id:
            self.record_id = uuid.uuid4()
