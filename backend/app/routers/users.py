"""
Luigi Chat - Users Router
Admin user management and user preferences
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID

from app.models import get_db
from app.models.database import User
from app.routers.auth import get_current_user
from app.services.litellm import litellm_service
from app.config import settings

router = APIRouter()


class UserPreferences(BaseModel):
    theme: Optional[str] = None
    primary_color: Optional[str] = None
    font_size: Optional[str] = None
    compact_mode: Optional[bool] = None
    default_model: Optional[str] = None
    voice_enabled: Optional[bool] = None
    voice_id: Optional[str] = None
    speech_speed: Optional[str] = None
    speech_emotion: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    theme: str
    primary_color: str
    default_model: str
    voice_enabled: bool
    status: str
    litellm_key: Optional[str] = None


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"


class UpdateUserRequest(BaseModel):
    theme: Optional[str] = None
    primary_color: Optional[str] = None
    font_size: Optional[str] = None
    compact_mode: Optional[bool] = None
    default_model: Optional[str] = None
    voice_enabled: Optional[bool] = None
    voice_id: Optional[str] = None
    speech_speed: Optional[str] = None
    speech_emotion: Optional[str] = None
    status: Optional[str] = None


async def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all users (admin only)"""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    
    return [
        UserResponse(
            id=str(u.id),
            email=u.email,
            role=u.role,
            theme=u.theme,
            primary_color=u.primary_color,
            default_model=u.default_model,
            voice_enabled=u.voice_enabled,
            status=u.status,
            litellm_key=u.litellm_key
        )
        for u in users
    ]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create a new user (admin only)"""
    
    existing = await db.execute(select(User).where(User.email == request.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    from app.utils.auth import hash_password
    from app.routers.auth import MODEL_ALIASES
    
    password_hash = hash_password(request.password)
    
    try:
        litellm_user = await litellm_service.create_user(request.email)
        litellm_user_id = litellm_user.get("user_id")
        
        key_response = await litellm_service.generate_key(
            user_id=litellm_user_id,
            models=list(MODEL_ALIASES.keys()),
            rpm_limit=settings.DEFAULT_RPM_LIMIT,
            tpm_limit=settings.DEFAULT_TPM_LIMIT,
            aliases=MODEL_ALIASES
        )
        api_key = key_response.get("key")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to create API key"
        )
    
    user = User(
        email=request.email,
        password_hash=password_hash,
        role=request.role,
        litellm_key=api_key,
        litellm_user_id=litellm_user_id,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        theme=user.theme,
        primary_color=user.primary_color,
        default_model=user.default_model,
        voice_enabled=user.voice_enabled,
        status=user.status,
        litellm_key=api_key
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID (admin or self)"""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        theme=user.theme,
        primary_color=user.primary_color,
        default_model=user.default_model,
        voice_enabled=user.voice_enabled,
        status=user.status,
        litellm_key=user.litellm_key if current_user.role == "admin" else None
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user preferences (admin or self)"""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        theme=user.theme,
        primary_color=user.primary_color,
        default_model=user.default_model,
        voice_enabled=user.voice_enabled,
        status=user.status
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a user (admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.delete(user)
    await db.commit()
