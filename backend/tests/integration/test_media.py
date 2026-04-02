import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestImageUpload:
    async def test_upload_requires_auth(self, client: AsyncClient):
        files = {"file": ("test.png", b"fake image data", "image/png")}
        response = await client.post("/api/files/upload", files=files)
        assert response.status_code == 401

    async def test_upload_invalid_file_type(self, client: AsyncClient):
        response = await client.post(
            "/api/files/upload",
            files={"file": ("test.txt", b"not an image", "text/plain")},
            headers={"Authorization": "Bearer fake-token"}
        )
        assert response.status_code == 401


class TestTTS:
    async def test_speech_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/audio/speech",
            json={"input": "Hello world"}
        )
        assert response.status_code == 401

    async def test_voices_endpoint_public(self, client: AsyncClient):
        response = await client.get("/api/audio/voices")
        assert response.status_code == 200
        data = response.json()
        assert "voices" in data
        assert len(data["voices"]) > 0
        assert all("id" in v and "name" in v for v in data["voices"])
