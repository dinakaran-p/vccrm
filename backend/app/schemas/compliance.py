from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class ComplianceStatusEnum(str, Enum):
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    PENDING_REVIEW = "Pending Review"
    EXEMPTED = "Exempted"

class EntityTypeEnum(str, Enum):
    FUND = "Fund"
    LP = "LP"
    PORTFOLIO = "Portfolio"

class ComplianceRecordBase(BaseModel):
    entity_type: EntityTypeEnum
    lp_id: Optional[UUID] = None
    compliance_type: str
    compliance_status: ComplianceStatusEnum = ComplianceStatusEnum.PENDING_REVIEW
    due_date: Optional[datetime] = None
    comments: Optional[str] = None

class ComplianceRecordCreate(ComplianceRecordBase):
    pass

class ComplianceRecordUpdate(BaseModel):
    compliance_status: Optional[ComplianceStatusEnum] = None
    due_date: Optional[datetime] = None
    comments: Optional[str] = None

class ComplianceRecordResponse(ComplianceRecordBase):
    record_id: UUID
    last_updated: datetime
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ComplianceRecordList(BaseModel):
    records: List[ComplianceRecordResponse]
    total: int
