from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID

# LP Details Schemas
class LPDetailsBase(BaseModel):
    lp_name: str
    mobile_no: Optional[str] = None
    email: EmailStr
    address: Optional[str] = None
    nominee: Optional[str] = None
    pan: Optional[str] = None
    dob: Optional[date] = None
    doi: Optional[date] = None
    gender: Optional[str] = None
    date_of_agreement: Optional[date] = None
    commitment_amount: Optional[float] = None
    acknowledgement_of_ppm: Optional[bool] = False
    dpid: Optional[str] = None
    client_id: Optional[str] = None
    cml: Optional[str] = None
    isin: Optional[str] = None
    class_of_shares: Optional[str] = None
    citizenship: Optional[str] = None
    type: Optional[str] = None
    geography: Optional[str] = None

class LPDetailsCreate(LPDetailsBase):
    pass

class LPDetailsUpdate(LPDetailsBase):
    lp_name: Optional[str] = None
    email: Optional[EmailStr] = None

class LPDetailsResponse(LPDetailsBase):
    lp_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# LP Drawdown Schemas
class LPDrawdownBase(BaseModel):
    lp_id: UUID
    drawdown_date: date
    amount: float
    drawdown_percentage: Optional[float] = None
    payment_due_date: date
    payment_received_date: Optional[date] = None
    payment_status: str = "Pending"
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class LPDrawdownCreate(LPDrawdownBase):
    pass

class LPDrawdownUpdate(BaseModel):
    drawdown_date: Optional[date] = None
    amount: Optional[float] = None
    drawdown_percentage: Optional[float] = None
    payment_due_date: Optional[date] = None
    payment_received_date: Optional[date] = None
    payment_status: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class LPDrawdownResponse(LPDrawdownBase):
    drawdown_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# LP List Response with Drawdowns
class LPWithDrawdowns(LPDetailsResponse):
    drawdowns: List[LPDrawdownResponse] = []
