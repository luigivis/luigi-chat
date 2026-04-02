"""
Luigi Chat - MiniMax API Service
Direct client for MiniMax API operations
"""
import httpx
import logging
from typing import Optional, Dict, Any, BinaryIO
from app.config import settings

logger = logging.getLogger(__name__)


class MiniMaxService:
    """Service for interacting with MiniMax API"""
    
    def __init__(self):
        self.base_url = settings.MINIMAX_API_BASE_URL
        self.api_key = settings.MINIMAX_API_KEY
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for MiniMax API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        purpose: str = "fine-tune"
    ) -> Dict[str, Any]:
        """Upload a file to MiniMax"""
        async with httpx.AsyncClient() as client:
            try:
                files = {"file": (filename, file)}
                data = {"purpose": purpose}
                
                response = await client.post(
                    f"{self.base_url}/v1/files/upload",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files=files,
                    data=data,
                    timeout=300.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error uploading file to MiniMax: {e}")
                raise
    
    async def list_files(self) -> Dict[str, Any]:
        """List all files in MiniMax"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/v1/files",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error listing MiniMax files: {e}")
                raise
    
    async def get_file(self, file_id: str) -> Dict[str, Any]:
        """Get information about a file"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/v1/files/{file_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error getting MiniMax file: {e}")
                raise
    
    async def get_file_content(self, file_id: str) -> bytes:
        """Download file content from MiniMax"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/v1/files/{file_id}/content",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.content
            except httpx.HTTPError as e:
                logger.error(f"Error getting MiniMax file content: {e}")
                raise
    
    async def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete a file from MiniMax"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.base_url}/v1/files/{file_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error deleting MiniMax file: {e}")
                raise
    
    async def text_to_speech(
        self,
        text: str,
        model: str = "speech-2.6-hd",
        voice_id: str = "male-qn-qingse",
        speed: float = 1.0,
        emotion: str = "neutral",
        format: str = "mp3",
        stream: bool = False
    ) -> Dict[str, Any]:
        """Convert text to speech using MiniMax Speech API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/t2a_v2",
                    headers=self._get_headers(),
                    json={
                        "model": model,
                        "text": text,
                        "stream": stream,
                        "voice_setting": {
                            "voice_id": voice_id,
                            "speed": speed,
                            "pitch": 0,
                            "volume": 0,
                            "emotion": emotion
                        },
                        "audio_setting": {
                            "sample_rate": 32000,
                            "bitrate": 128000,
                            "format": format
                        }
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error in TTS: {e}")
                raise


minimax_service = MiniMaxService()
