"""
Luigi Chat - Audio Router
Text-to-Speech using MiniMax Speech 2.6
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import logging

from app.models.database import User
from app.routers.auth import get_current_user
from app.services.minimax import minimax_service
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class SpeechRequest(BaseModel):
    input: str
    model: Optional[str] = "luigi-voice"
    voice_id: Optional[str] = None
    speed: Optional[float] = 1.0
    emotion: Optional[str] = "neutral"
    format: Optional[str] = "mp3"


@router.post("/speech")
async def text_to_speech(
    request: SpeechRequest,
    current_user: User = Depends(get_current_user)
):
    """Convert text to speech using MiniMax Speech 2.6"""
    
    voice_id = request.voice_id or current_user.voice_id or settings.DEFAULT_VOICE_ID
    speed = request.speed or float(current_user.speech_speed) or settings.DEFAULT_SPEECH_SPEED
    emotion = request.emotion or current_user.speech_emotion or settings.DEFAULT_SPEECH_EMOTION
    
    model_map = {
        "luigi-voice": "speech-2.6-hd"
    }
    
    minimax_model = model_map.get(request.model, "speech-2.6-hd")
    
    try:
        response = await minimax_service.text_to_speech(
            text=request.input,
            model=minimax_model,
            voice_id=voice_id,
            speed=speed,
            emotion=emotion,
            format=request.format or "mp3"
        )
        
        if "audio_file" in response:
            audio_url = response["audio_file"]
            return {"audio_url": audio_url}
        
        return response
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS failed: {str(e)}"
        )


@router.get("/voices")
async def list_voices():
    """List available voices"""
    
    voices = [
        {"id": "male-qn-qingse", "name": "Male Qingse", "gender": "male"},
        {"id": "female-qn-qingse", "name": "Female Qingse", "gender": "female"},
        {"id": "male-qn-tianmei", "name": "Male Tianmei", "gender": "male"},
        {"id": "female-qn-tianmei", "name": "Female Tianmei", "gender": "female"},
        {"id": "male-qn-yunyang", "name": "Male Yunyang", "gender": "male"},
        {"id": "female-qn-yunyang", "name": "Female Yunyang", "gender": "female"},
        {"id": "male-qn-john", "name": "Male John", "gender": "male"},
        {"id": "female-qn-emma", "name": "Female Emma", "gender": "female"},
    ]
    
    return {"voices": voices}
