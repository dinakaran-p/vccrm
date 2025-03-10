from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database.base import get_db
from app.models.compliance_records import ComplianceRecord, EntityType, ComplianceStatus
from app.schemas.compliance import (
    ComplianceRecordCreate, ComplianceRecordUpdate, ComplianceRecordResponse,
    ComplianceRecordList, EntityTypeEnum, ComplianceStatusEnum
)
from app.auth.security import get_current_user
from app.utils.audit import log_activity
import uuid
from sqlalchemy import func

router = APIRouter()

@router.post("/records", response_model=ComplianceRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_compliance_record(
    record_data: ComplianceRecordCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new compliance record.
    """
    # Check if user has appropriate role
    if current_user.get("role") not in ["Fund Manager", "Compliance Officer", "Fund Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have one of the required roles: Fund Manager, Compliance Officer, Fund Admin"
        )
    
    try:
        # Print the current_user dictionary to see what keys are available
        print(f"Current user: {current_user}")
        
        # Use 'sub' instead of 'user_id' and provide a default UUID if not found
        user_id = current_user.get("sub", "00000000-0000-0000-0000-000000000000")
        print(f"User ID: {user_id}")
        
        # Create new compliance record
        new_record = ComplianceRecord(
            entity_type=record_data.entity_type.value,
            lp_id=record_data.lp_id,
            compliance_type=record_data.compliance_type,
            compliance_status=record_data.compliance_status.value,
            due_date=record_data.due_date,
            comments=record_data.comments,
        )
        
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        
        # Log the activity
        try:
            log_activity(
                db=db, 
                activity="compliance_record_created", 
                details=f"Created compliance record: {record_data.compliance_type} for {record_data.entity_type.value}"
            )
        except Exception as e:
            print(f"Error logging activity: {str(e)}")
            # Continue even if logging fails
        
        return new_record
    except Exception as e:
        db.rollback()
        print(f"Error creating compliance record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating compliance record: {str(e)}"
        )

@router.get("/records", response_model=ComplianceRecordList)
async def get_compliance_records(
    entity_type: Optional[EntityTypeEnum] = None,
    lp_id: Optional[uuid.UUID] = None,
    compliance_status: Optional[ComplianceStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get compliance records with optional filtering.
    """
    query = db.query(ComplianceRecord)
    
    if entity_type:
        query = query.filter(ComplianceRecord.entity_type == entity_type.value)
    
    if lp_id:
        query = query.filter(ComplianceRecord.lp_id == lp_id)
    
    if compliance_status:
        query = query.filter(ComplianceRecord.compliance_status == compliance_status.value)
    
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    
    return ComplianceRecordList(records=records, total=total)

@router.get("/records/{record_id}", response_model=ComplianceRecordResponse)
async def get_compliance_record(
    record_id: uuid.UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific compliance record by ID.
    """
    record = db.query(ComplianceRecord).filter(ComplianceRecord.record_id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance record not found"
        )
    return record

@router.put("/records/{record_id}", response_model=ComplianceRecordResponse)
async def update_compliance_record(
    record_id: uuid.UUID,
    record_data: ComplianceRecordUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing compliance record.
    """
    # Check if user has appropriate role
    if current_user.get("role") not in ["Fund Manager", "Compliance Officer", "Fund Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have one of the required roles: Fund Manager, Compliance Officer, Fund Admin"
        )
    
    record = db.query(ComplianceRecord).filter(ComplianceRecord.record_id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance record not found"
        )
    
    # Update record data
    update_data = record_data.model_dump(exclude_unset=True)
    
    if "compliance_status" in update_data and update_data["compliance_status"]:
        update_data["compliance_status"] = update_data["compliance_status"].value
    
    for key, value in update_data.items():
        setattr(record, key, value)
    
    # Update the updated_by field
    record.updated_by = uuid.UUID(current_user["user_id"])
    
    db.commit()
    db.refresh(record)
    
    # Log the activity
    try:
        # Convert user_id to UUID or use a default UUID if conversion fails
        try:
            user_uuid = uuid.UUID(current_user["sub"])
        except (KeyError, ValueError):
            user_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")
            
        log_activity(
            db=db, 
            activity="compliance_record_updated", 
            user_id=user_uuid, 
            details=f"Updated compliance record: {record_id}"
        )
    except Exception as e:
        print(f"Error logging activity: {str(e)}")
        # Continue even if logging fails
    
    return record

@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_compliance_record(
    record_id: uuid.UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a compliance record.
    """
    # Check if user has appropriate role
    if current_user.get("role") not in ["Fund Manager", "Compliance Officer", "Fund Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have one of the required roles: Fund Manager, Compliance Officer, Fund Admin"
        )
    
    record = db.query(ComplianceRecord).filter(ComplianceRecord.record_id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance record not found"
        )
    
    db.delete(record)
    db.commit()
    
    # Log the activity
    try:
        # Convert user_id to UUID or use a default UUID if conversion fails
        try:
            user_uuid = uuid.UUID(current_user["sub"])
        except (KeyError, ValueError):
            user_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")
            
        log_activity(
            db=db, 
            activity="compliance_record_deleted", 
            user_id=user_uuid, 
            details=f"Deleted compliance record: {record_id}"
        )
    except Exception as e:
        print(f"Error logging activity: {str(e)}")
        # Continue even if logging fails
    
    return None

@router.get("/stats", response_model=Dict[str, Any])
async def get_compliance_stats(
    entity_type: Optional[EntityTypeEnum] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get compliance statistics.
    """
    query = db.query(ComplianceRecord)
    
    if entity_type:
        query = query.filter(ComplianceRecord.entity_type == entity_type.value)
    
    total = query.count()
    compliant = query.filter(ComplianceRecord.compliance_status == ComplianceStatus.COMPLIANT.value).count()
    non_compliant = query.filter(ComplianceRecord.compliance_status == ComplianceStatus.NON_COMPLIANT.value).count()
    pending = query.filter(ComplianceRecord.compliance_status == ComplianceStatus.PENDING_REVIEW.value).count()
    exempted = query.filter(ComplianceRecord.compliance_status == ComplianceStatus.EXEMPTED.value).count()
    
    return {
        "total": total,
        "compliant": compliant,
        "non_compliant": non_compliant,
        "pending_review": pending,
        "exempted": exempted,
        "compliance_rate": (compliant / total * 100) if total > 0 else 0
    }
