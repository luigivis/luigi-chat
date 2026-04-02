"""
Luigi Chat - Files Router
MiniMax File API proxy for file management
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from fastapi import status
from uuid import UUID
import logging

from app.models import get_db
from app.models.database import File as FileModel, User
from app.routers.auth import get_current_user
from app.services.minimax import minimax_service

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_DOCUMENT_TYPES = {"pdf", "docx", "txt", "jsonl"}
ALLOWED_AUDIO_TYPES = {"mp3", "m4a", "wav"}
MAX_FILE_SIZE = 512 * 1024 * 1024  # 512MB


class FileResponse(BaseModel):
    id: str
    user_id: str
    minimax_file_id: str
    filename: str
    file_type: str
    size_bytes: int
    status: str
    created_at: Optional[str]


@router.get("/", response_model=List[FileResponse])
async def list_files(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all files for current user"""
    result = await db.execute(
        select(FileModel)
        .where(FileModel.user_id == current_user.id, FileModel.status == "active")
        .order_by(FileModel.created_at.desc())
    )
    files = result.scalars().all()
    
    return [to_file_response(f) for f in files]


@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a file to MiniMax"""
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size is {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    content = await file.read()
    
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext in ALLOWED_DOCUMENT_TYPES:
        file_type = "document"
    elif file_ext in ALLOWED_AUDIO_TYPES:
        file_type = "audio"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {ALLOWED_DOCUMENT_TYPES | ALLOWED_AUDIO_TYPES}"
        )
    
    try:
        minimax_response = await minimax_service.upload_file(
            file=content,
            filename=file.filename,
            purpose="fine-tune"
        )
        minimax_file_id = minimax_response.get("id")
        
    except Exception as e:
        logger.error(f"MiniMax upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to upload file to MiniMax"
        )
    
    db_file = FileModel(
        user_id=current_user.id,
        minimax_file_id=minimax_file_id,
        filename=file.filename,
        file_type=file_type,
        size_bytes=len(content)
    )
    
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    
    return to_file_response(db_file)


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get file metadata"""
    result = await db.execute(
        select(FileModel).where(
            FileModel.id == file_id,
            FileModel.user_id == current_user.id
        )
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return to_file_response(file)


@router.get("/{file_id}/content")
async def download_file_content(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download file content from MiniMax"""
    result = await db.execute(
        select(FileModel).where(
            FileModel.id == file_id,
            FileModel.user_id == current_user.id
        )
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        content = await minimax_service.get_file_content(file.minimax_file_id)
        
        media_type = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain",
            "jsonl": "application/jsonl",
            "mp3": "audio/mpeg",
            "m4a": "audio/mp4",
            "wav": "audio/wav",
        }.get(file.filename.split(".")[-1].lower(), "application/octet-stream")
        
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{file.filename}"'}
        )
        
    except Exception as e:
        logger.error(f"MiniMax download error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to download file"
        )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a file (soft delete)"""
    result = await db.execute(
        select(FileModel).where(
            FileModel.id == file_id,
            FileModel.user_id == current_user.id
        )
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        await minimax_service.delete_file(file.minimax_file_id)
    except Exception as e:
        logger.warning(f"Failed to delete from MiniMax: {e}")
    
    file.status = "deleted"
    await db.commit()


def to_file_response(file: FileModel) -> FileResponse:
    return FileResponse(
        id=str(file.id),
        user_id=str(file.user_id),
        minimax_file_id=file.minimax_file_id,
        filename=file.filename,
        file_type=file.file_type,
        size_bytes=file.size_bytes,
        status=file.status,
        created_at=file.created_at.isoformat() if file.created_at else None
    )
