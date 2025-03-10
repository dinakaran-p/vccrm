from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database.base import get_db
from app.models.lp_details import LPDetails
from app.models.lp_drawdowns import LPDrawdown
from app.schemas.lp import (
    LPDetailsCreate, LPDetailsUpdate, LPDetailsResponse, 
    LPDrawdownCreate, LPDrawdownUpdate, LPDrawdownResponse,
    LPWithDrawdowns
)
from app.auth.security import get_current_user, check_role
from app.utils.audit import log_activity
import uuid
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse

router = APIRouter()

# LP Details Endpoints
@router.post("/", response_model=LPDetailsResponse, status_code=status.HTTP_201_CREATED)
async def create_lp(
    lp_data: LPDetailsCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new LP (Limited Partner) record.
    """
    # Check if user has appropriate role
    if current_user.get("role") not in ["Fund Manager", "Compliance Officer", "Fund Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have one of the required roles: Fund Manager, Compliance Officer, Fund Admin"
        )
    
    # Create new LP record
    new_lp = LPDetails(**lp_data.model_dump())
    
    try:
        db.add(new_lp)
        db.commit()
        db.refresh(new_lp)
        
        # Log the activity
        try:
            # Print the current_user dictionary to see what keys are available
            print(f"Current user: {current_user}")
            
            log_activity(
                db=db, 
                activity="lp_created", 
                user_id=uuid.UUID(current_user.get("sub", "00000000-0000-0000-0000-000000000000")), 
                details=f"Created LP: {new_lp.lp_name}"
            )
        except Exception as e:
            print(f"Error logging activity: {str(e)}")
            # Continue even if logging fails
        
        return new_lp
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LP with this email or PAN already exists"
        )

@router.get("/", response_model=List[LPDetailsResponse])
async def get_all_lps(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all LP records with pagination.
    """
    lps = db.query(LPDetails).offset(skip).limit(limit).all()
    return lps

@router.get("/{lp_id}", response_model=LPWithDrawdowns)
async def get_lp(
    lp_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific LP record by ID, including their drawdowns.
    """
    lp = db.query(LPDetails).filter(LPDetails.lp_id == lp_id).first()
    if not lp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LP not found"
        )
    return lp

@router.put("/{lp_id}", response_model=LPDetailsResponse)
async def update_lp(
    lp_id: uuid.UUID,
    lp_data: LPDetailsUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing LP record.
    """
    # Check if user has appropriate role
    check_role(["Fund Manager", "Compliance Officer", "Fund Admin"])
    
    lp = db.query(LPDetails).filter(LPDetails.lp_id == lp_id).first()
    if not lp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LP not found"
        )
    
    # Update LP data
    update_data = lp_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lp, key, value)
    
    try:
        db.commit()
        db.refresh(lp)
        
        # Log the activity
        try:
            # Print the current_user dictionary to see what keys are available
            print(f"Current user: {get_current_user()}")
            
            log_activity(
                db=db, 
                activity="lp_updated", 
                user_id=uuid.UUID(get_current_user().get("sub", "00000000-0000-0000-0000-000000000000")), 
                details=f"Updated LP: {lp.lp_name}"
            )
        except Exception as e:
            print(f"Error logging activity: {str(e)}")
            # Continue even if logging fails
        
        return lp
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LP with this email or PAN already exists"
        )

@router.delete("/{lp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lp(
    lp_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an LP record.
    """
    # Check if user has appropriate role
    check_role(["Fund Manager", "Fund Admin"])
    
    lp = db.query(LPDetails).filter(LPDetails.lp_id == lp_id).first()
    if not lp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LP not found"
        )
    
    # Log before deletion
    lp_name = lp.lp_name
    
    db.delete(lp)
    db.commit()
    
    # Log the activity
    try:
        # Print the current_user dictionary to see what keys are available
        print(f"Current user: {get_current_user()}")
        
        log_activity(
            db=db, 
            activity="lp_deleted", 
            user_id=uuid.UUID(get_current_user().get("sub", "00000000-0000-0000-0000-000000000000")), 
            details=f"Deleted LP: {lp_name}"
        )
    except Exception as e:
        print(f"Error logging activity: {str(e)}")
        # Continue even if logging fails
    
    return None

# LP Drawdown Endpoints
@router.post("/drawdowns", response_model=LPDrawdownResponse, status_code=status.HTTP_201_CREATED)
async def create_drawdown(
    drawdown_data: LPDrawdownCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new drawdown record for an LP.
    """
    # Check if user has appropriate role
    check_role(["Fund Manager", "Fund Admin"])
    
    # Check if LP exists
    lp = db.query(LPDetails).filter(LPDetails.lp_id == drawdown_data.lp_id).first()
    if not lp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LP not found"
        )
    
    # Create new drawdown
    new_drawdown = LPDrawdown(**drawdown_data.model_dump())
    
    db.add(new_drawdown)
    db.commit()
    db.refresh(new_drawdown)
    
    # Log the activity
    try:
        user = await get_current_user()
        # Print the current_user dictionary to see what keys are available
        print(f"Current user: {user}")
        
        log_activity(
            db=db, 
            activity="drawdown_created", 
            user_id=uuid.UUID(get_current_user().get("sub", "00000000-0000-0000-0000-000000000000")), 
            details=f"Created drawdown for LP: {lp.lp_name}, Amount: {new_drawdown.amount}"
        )
    except Exception as e:
        print(f"Error logging activity: {str(e)}")
        # Continue even if logging fails
    
    return new_drawdown

@router.get("/drawdowns/list", response_model=List[LPDrawdownResponse])
async def get_all_drawdowns(
    lp_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all drawdown records with optional filtering by LP.
    """
    print("Getting drawdowns with lp_id:", lp_id)
    query = db.query(LPDrawdown)
    
    if lp_id:
        query = query.filter(LPDrawdown.lp_id == lp_id)
    
    drawdowns = query.offset(skip).limit(limit).all()
    return drawdowns

@router.get("/drawdowns/{drawdown_id}", response_model=LPDrawdownResponse)
async def get_drawdown(
    drawdown_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific drawdown record by ID.
    """
    drawdown = db.query(LPDrawdown).filter(LPDrawdown.drawdown_id == drawdown_id).first()
    if not drawdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drawdown not found"
        )
    return drawdown

@router.put("/drawdowns/{drawdown_id}", response_model=LPDrawdownResponse)
async def update_drawdown(
    drawdown_id: uuid.UUID,
    drawdown_data: LPDrawdownUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing drawdown record.
    """
    # Check if user has appropriate role
    check_role(["Fund Manager", "Fund Admin"])
    
    drawdown = db.query(LPDrawdown).filter(LPDrawdown.drawdown_id == drawdown_id).first()
    if not drawdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drawdown not found"
        )
    
    # Update drawdown data
    update_data = drawdown_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(drawdown, key, value)
    
    db.commit()
    db.refresh(drawdown)
    
    # Log the activity
    try:
        # Print the current_user dictionary to see what keys are available
        print(f"Current user: {get_current_user()}")
        
        log_activity(
            db=db, 
            activity="drawdown_updated", 
            user_id=uuid.UUID(get_current_user().get("sub", "00000000-0000-0000-0000-000000000000")), 
            details=f"Updated drawdown: {drawdown_id}"
        )
    except Exception as e:
        print(f"Error logging activity: {str(e)}")
        # Continue even if logging fails
    
    return drawdown

@router.delete("/drawdowns/{drawdown_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_drawdown(
    drawdown_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a drawdown record.
    """
    # Check if user has appropriate role
    check_role(["Fund Manager", "Fund Admin"])
    
    drawdown = db.query(LPDrawdown).filter(LPDrawdown.drawdown_id == drawdown_id).first()
    if not drawdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drawdown not found"
        )
    
    db.delete(drawdown)
    db.commit()
    
    # Log the activity
    try:
        # Print the current_user dictionary to see what keys are available
        print(f"Current user: {get_current_user()}")
        
        log_activity(
            db=db, 
            activity="drawdown_deleted", 
            user_id=uuid.UUID(get_current_user().get("sub", "00000000-0000-0000-0000-000000000000")), 
            details=f"Deleted drawdown: {drawdown_id}"
        )
    except Exception as e:
        print(f"Error logging activity: {str(e)}")
        # Continue even if logging fails
    
    return None
