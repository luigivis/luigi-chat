import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestChats:
    async def test_get_chats_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/chats/")
        assert response.status_code == 401

    async def test_create_chat_unauthorized(self, client: AsyncClient):
        response = await client.post("/api/chats/", json={"title": "Test Chat"})
        assert response.status_code == 401


class TestMessages:
    async def test_get_messages_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/chats/test-id/messages")
        assert response.status_code == 401

    async def test_send_message_unauthorized(self, client: AsyncClient):
        response = await client.post(
            "/api/chats/test-id/messages",
            json={"content": "Hello"}
        )
        assert response.status_code == 401


class TestFiles:
    async def test_upload_file_unauthorized(self, client: AsyncClient):
        response = await client.post("/api/files/upload")
        assert response.status_code == 401

    async def test_list_files_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/files/")
        assert response.status_code == 401


class TestAudio:
    async def test_speech_unauthorized(self, client: AsyncClient):
        response = await client.post(
            "/api/audio/speech",
            json={"input": "Hello"}
        )
        assert response.status_code == 401

    async def test_list_voices(self, client: AsyncClient):
        response = await client.get("/api/audio/voices")
        assert response.status_code == 200
        data = response.json()
        assert "voices" in data
        assert len(data["voices"]) > 0


class TestModels:
    async def test_list_models(self, client: AsyncClient):
        response = await client.get("/api/models/")
        assert response.status_code == 401
