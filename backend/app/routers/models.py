"""
Luigi Chat - Models Router
Available models information
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from app.models.database import User
from app.routers.auth import get_current_user

router = APIRouter()


class ModelInfo(BaseModel):
    id: str
    name: str
    description: str
    context_window: int
    supports_vision: bool
    supports_streaming: bool
    modality: str = "text"


class ModelsResponse(BaseModel):
    models: List[ModelInfo]


MODELS = [
    ModelInfo(
        id="luigi-thinking",
        name="MiniMax M2.7",
        description="Chat principal con razonamiento avanzado. Excelente para coding, razonamiento complejo y tareas de ingenieria.",
        context_window=204800,
        supports_vision=False,
        supports_streaming=True,
        modality="text"
    ),
    ModelInfo(
        id="luigi-vision",
        name="MiniMax Text-01",
        description="Analisis de imagenes. Puede entender y analizar imagenes, diagrams, y documentos.",
        context_window=100000,
        supports_vision=True,
        supports_streaming=True,
        modality="text"
    ),
    ModelInfo(
        id="luigi-voice",
        name="MiniMax Speech 2.6 HD",
        description="Text-to-Speech con voz natural. Latencia ultra-baja (<250ms), 40+ idiomas, control de emociones.",
        context_window=0,
        supports_vision=False,
        supports_streaming=True,
        modality="audio"
    )
]


@router.get("/", response_model=ModelsResponse)
async def list_models(current_user: User = Depends(get_current_user)):
    """List available models"""
    return ModelsResponse(models=MODELS)
