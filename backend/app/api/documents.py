from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from app.database.base import get_db
from app.models.document import Document, TaskDocument, DocumentStatus, DocumentCategory
from app.models.user import User
from app.models.compliance_task import ComplianceTask
from app.schemas.document import (
    Document as DocumentSchema,
    DocumentCreate,
    DocumentUpdate,
    TaskDocumentCreate,
    TaskDocument as TaskDocumentSchema
)
from app.utils.file_storage import save_upload_file
from app.auth.security import get_current_user
from app.utils.audit import log_activity

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=DocumentSchema, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    name: str = Form(...),
    category: str = Form(...),
    expiry_date: Optional[str] = Form(None),
    process_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload a new document with metadata.
    Only users with roles Fund Manager, Compliance Officer, or Admin can upload documents.
    """
    # Check if user has permission to upload documents
    if current_user.get('role') not in ["Fund Manager", "Compliance Officer", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload documents"
        )
    
    try:
        # Save the file to local storage
        file_path = save_upload_file(file, category)
        
        # Create a new document record in the database
        db_document = Document(
            name=name,
            category=category,
            file_path=file_path,
            status=DocumentStatus.ACTIVE,
            process_id=process_id
        )
        
        if expiry_date:
            db_document.expiry_date = expiry_date
            
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Log document upload activity
        user_id = None
        if "sub" in current_user:
            user = db.query(User).filter(User.email == current_user["sub"]).first()
            if user:
                user_id = user.user_id
                
        log_activity(
            db, 
            "document_upload", 
            user_id, 
            f"Document uploaded: {db_document.document_id} - {name} ({category})"
        )
        
        return db_document
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )

@router.get("/", response_model=List[DocumentSchema])
async def list_documents(
    category: Optional[str] = Query(None, description="Filter by document category"),
    status: Optional[str] = Query(None, description="Filter by document status"),
    name: Optional[str] = Query(None, description="Filter by document name"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List all documents with optional filters.
    """
    query = db.query(Document)
    
    # Apply filters if provided
    if category:
        query = query.filter(Document.category == category)
    if status:
        query = query.filter(Document.status == status)
    if name:
        query = query.filter(Document.name.ilike(f"%{name}%"))
    
    documents = query.all()
    return documents

@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a specific document by ID.
    """
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return document

@router.post("/{document_id}/link-to-task", response_model=TaskDocumentSchema)
async def link_document_to_task(
    document_id: UUID,
    task_link: TaskDocumentCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Link a document to a compliance task.
    """
    # Verify document exists
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Verify task exists
    task = db.query(ComplianceTask).filter(ComplianceTask.compliance_task_id == task_link.compliance_task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compliance task with ID {task_link.compliance_task_id} not found"
        )
    
    # Check if link already exists
    existing_link = db.query(TaskDocument).filter(
        and_(
            TaskDocument.document_id == document_id,
            TaskDocument.compliance_task_id == task_link.compliance_task_id
        )
    ).first()
    
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This document is already linked to the specified task"
        )
    
    # Create the link
    task_document = TaskDocument(
        compliance_task_id=task_link.compliance_task_id,
        document_id=document_id
    )
    
    db.add(task_document)
    db.commit()
    db.refresh(task_document)
    
    # Log document link activity
    user_id = None
    if "sub" in current_user:
        user = db.query(User).filter(User.email == current_user["sub"]).first()
        if user:
            user_id = user.user_id
            
    log_activity(
        db, 
        "document_task_link", 
        user_id, 
        f"Document {document_id} linked to task {task_link.compliance_task_id}"
    )
    
    return task_document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a document (only for Admin users).
    """
    # Only Admin users can delete documents
    if current_user.get('role') != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin users can delete documents"
        )
    
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Delete all task document links first
    db.query(TaskDocument).filter(TaskDocument.document_id == document_id).delete()
    
    # Delete the document
    db.delete(document)
    db.commit()
    
    logger.info(f"Document {document_id} deleted by user {current_user.get('sub')}")
    return None
