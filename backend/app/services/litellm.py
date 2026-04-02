"""
Luigi Chat - LiteLLM Service
Wrapper for LiteLLM Proxy operations
"""
import httpx
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class LiteLLMService:
    """Service for interacting with LiteLLM Proxy"""
    
    def __init__(self):
        self.base_url = settings.LITELLM_PROXY_URL
        self.master_key = settings.LITELLM_MASTER_KEY
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for LiteLLM API requests"""
        return {
            "Authorization": f"Bearer {self.master_key}",
            "Content-Type": "application/json"
        }
    
    async def create_user(self, user_email: str) -> Dict[str, Any]:
        """Create a user in LiteLLM"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/user/new",
                    headers=self._get_headers(),
                    json={"user_email": user_email}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error creating LiteLLM user: {e}")
                raise
    
    async def generate_key(
        self,
        user_id: str,
        models: list,
        rpm_limit: int = 3,
        tpm_limit: int = 6000,
        aliases: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate an API key for a user"""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "user_id": user_id,
                    "models": models,
                    "rpm_limit": rpm_limit,
                    "tpm_limit": tpm_limit,
                }
                if aliases:
                    payload["aliases"] = aliases
                
                response = await client.post(
                    f"{self.base_url}/key/generate",
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error generating LiteLLM key: {e}")
                raise
    
    async def get_key_info(self, key: str) -> Dict[str, Any]:
        """Get information about a key"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/key/info",
                    headers=self._get_headers(),
                    params={"key": key}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error getting key info: {e}")
                raise
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information from LiteLLM"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/user/info",
                    headers=self._get_headers(),
                    params={"user_id": user_id}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error getting LiteLLM user info: {e}")
                raise
    
    async def chat_completion(
        self,
        api_key: str,
        model: str,
        messages: list,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Make a chat completion request through LiteLLM"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": stream
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error in chat completion: {e}")
                raise
    
    async def block_key(self, key: str) -> Dict[str, Any]:
        """Block a key"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/key/block",
                    headers=self._get_headers(),
                    json={"key": key}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error blocking key: {e}")
                raise
    
    async def unblock_key(self, key: str) -> Dict[str, Any]:
        """Unblock a key"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/key/unblock",
                    headers=self._get_headers(),
                    json={"key": key}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error unblocking key: {e}")
                raise


litellm_service = LiteLLMService()
