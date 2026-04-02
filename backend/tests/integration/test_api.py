import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestHealth:
    async def test_health_endpoint(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAuth:
    async def test_signup_missing_fields(self, client: AsyncClient):
        response = await client.post("/api/auth/signup", json={})
        assert response.status_code == 422

    async def test_login_missing_fields(self, client: AsyncClient):
        response = await client.post("/api/auth/login", json={})
        assert response.status_code == 422

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/auth/me")
        assert response.status_code == 401


class TestAudio:
    async def test_list_voices(self, client: AsyncClient):
        response = await client.get("/api/audio/voices")
        assert response.status_code == 200
        data = response.json()
        assert "voices" in data
        assert len(data["voices"]) > 0

    async def test_speech_requires_auth(self, client: AsyncClient):
        response = await client.post("/api/audio/speech", json={"input": "Hello"})
        assert response.status_code == 401


class TestModels:
    async def test_list_models(self, client: AsyncClient):
        response = await client.get("/api/models/")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
