import os
import shutil
from pathlib import Path
from fastapi import UploadFile
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

# Define the base directory for file storage
UPLOAD_DIR = Path("uploads")


def ensure_upload_directory():
    """Ensure that the upload directory exists."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_upload_file(upload_file: UploadFile, category: str) -> str:
    """
    Save an uploaded file to local storage.
    
    Args:
        upload_file: The file uploaded by the user
        category: The document category for organizing files
        
    Returns:
        The relative path where the file is stored
    """
    ensure_upload_directory()
    
    # Create a category subdirectory
    category_dir = UPLOAD_DIR / category
    category_dir.mkdir(exist_ok=True)
    
    # Generate a unique filename to avoid collisions
    original_filename = upload_file.filename
    file_extension = os.path.splitext(original_filename)[1] if original_filename else ""
    unique_filename = f"{uuid4()}{file_extension}"
    
    # Create the full path
    file_path = category_dir / unique_filename
    
    # Save the file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    logger.info(f"Saved file {original_filename} to {file_path}")
    
    # Return the relative path
    return str(file_path)


def delete_file(file_path: str) -> bool:
    """
    Delete a file from storage.
    
    Args:
        file_path: The path to the file to delete
        
    Returns:
        True if the file was deleted, False otherwise
    """
    try:
        path = Path(file_path)
        path.unlink(missing_ok=True)
        logger.info(f"Deleted file {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False
