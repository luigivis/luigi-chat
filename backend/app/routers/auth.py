"""
Luigi Chat - Auth Router
Handles user registration, login, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import timedelta
import logging

from app.models import get_db
from app.models.database import User
from app.utils.auth import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    decode_token
)
from app.services.litellm import litellm_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

MODEL_ALIASES = {
    "luigi-thinking": "minimax/MiniMax-M2.7",
    "luigi-vision": "minimax/MiniMax-Text-01",
    "luigi-voice": "minimax/speech-2.6-hd"
}


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class SignupResponse(BaseModel):
    id: str
    email: str
    role: str
    api_key: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    theme: str
    primary_color: str
    default_model: str
    voice_enabled: bool
    status: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user and auto-generate LiteLLM API key"""
    
    existing = await db.execute(select(User).where(User.email == request.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
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
        logger.error(f"LiteLLM error during signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to create API key. Please try again."
        )
    
    user = User(
        email=request.email,
        password_hash=password_hash,
        role="user",
        litellm_key=api_key,
        litellm_user_id=litellm_user_id,
        default_model=settings.DEFAULT_MODEL,
        voice_id=settings.DEFAULT_VOICE_ID,
        speech_speed=str(settings.DEFAULT_SPEECH_SPEED),
        speech_emotion=settings.DEFAULT_SPEECH_EMOTION,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return SignupResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        api_key=api_key
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        theme=current_user.theme,
        primary_color=current_user.primary_color,
        default_model=current_user.default_model,
        voice_enabled=current_user.voice_enabled,
        status=current_user.status
    )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    payload = decode_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled"
        )
    
    new_access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    return {
        "access_token": new_access_token,
        "token_type": "Bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
