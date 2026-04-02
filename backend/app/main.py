"""
Luigi Chat - Backend Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.database import engine, Base
from app.routers import auth, users, chats, files, audio, models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting Luigi Chat Backend...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created/verified")
    logger.info(f"LiteLLM Proxy URL: {settings.LITELLM_PROXY_URL}")
    logger.info(f"Minimax API Base: {settings.MINIMAX_API_BASE_URL}")
    
    yield
    
    logger.info("Shutting down Luigi Chat Backend...")


app = FastAPI(
    title=settings.WEBUI_NAME,
    description="Luigi Chat - AI Chat Interface with MiniMax",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(chats.router, prefix="/chats", tags=["chats"])
app.include_router(files.router, prefix="/files", tags=["files"])
app.include_router(audio.router, prefix="/audio", tags=["audio"])
app.include_router(models.router, prefix="/models", tags=["models"])


@app.get("/")
async def root():
    return {
        "name": settings.WEBUI_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG
    )
