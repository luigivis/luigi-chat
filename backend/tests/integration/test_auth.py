import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestAuthSignup:
    async def test_signup_missing_fields(self, client: AsyncClient):
        response = await client.post("/api/auth/signup", json={})
        assert response.status_code == 422

    async def test_signup_invalid_email(self, client: AsyncClient):
        response = await client.post("/api/auth/signup", json={
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422

    async def test_signup_password_too_short(self, client: AsyncClient):
        response = await client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "short"
        })
        assert response.status_code in [422, 400]


class TestAuthLogin:
    async def test_login_missing_fields(self, client: AsyncClient):
        response = await client.post("/api/auth/login", json={})
        assert response.status_code == 422

    async def test_login_invalid_email(self, client: AsyncClient):
        response = await client.post("/api/auth/login", json={
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422

    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        assert response.status_code == 401

    async def test_login_wrong_password(self, client: AsyncClient):
        response = await client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code in [401, 404]


class TestAuthMe:
    async def test_me_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    async def test_me_invalid_token(self, client: AsyncClient):
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401


class TestAuthRefresh:
    async def test_refresh_missing_token(self, client: AsyncClient):
        response = await client.post("/api/auth/refresh")
        assert response.status_code in [401, 422]

    async def test_refresh_invalid_token(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid-token"}
        )
        assert response.status_code == 401
