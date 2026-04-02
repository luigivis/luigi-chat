"""
Luigi Chat - Configuration Management
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App Info
    WEBUI_NAME: str = "Luigi Chat"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-change-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql://luigi:luigi_password@localhost:5432/luigi_chat"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # LiteLLM
    LITELLM_MASTER_KEY: str = "sk-dev-key"
    LITELLM_PROXY_URL: str = "http://localhost:4000"
    
    # MiniMax
    MINIMAX_API_KEY: str = ""
    MINIMAX_API_BASE_URL: str = "https://api.minimax.io"
    
    # Rate Limiting
    DEFAULT_RPM_LIMIT: int = 3
    DEFAULT_TPM_LIMIT: int = 6000
    DEFAULT_MAX_BUDGET: float = 100.0
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # JWT
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Default Model
    DEFAULT_MODEL: str = "luigi-thinking"
    
    # Default Voice Settings
    DEFAULT_VOICE_ID: str = "male-qn-qingse"
    DEFAULT_SPEECH_SPEED: float = 1.0
    DEFAULT_SPEECH_EMOTION: str = "neutral"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
