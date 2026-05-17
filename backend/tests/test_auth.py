import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_register(client):
    with patch("app.services.auth_service.send_otp_msg91", new_callable=AsyncMock):
        response = await client.post("/api/auth/register", json={
            "name": "Test User", "email": "test@example.com",
            "phone": "9876543210", "password": "TestPass123!", "role": "buyer"
        })
    assert response.status_code == 201
    data = response.json()["data"]
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    with patch("app.services.auth_service.send_otp_msg91", new_callable=AsyncMock):
        await client.post("/api/auth/register", json={
            "name": "User 2", "email": "dup@example.com",
            "phone": "9000000001", "password": "TestPass123!", "role": "buyer"
        })
        response = await client.post("/api/auth/register", json={
            "name": "User 2b", "email": "dup@example.com",
            "phone": "9000000002", "password": "TestPass123!", "role": "buyer"
        })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client):
    with patch("app.services.auth_service.send_otp_msg91", new_callable=AsyncMock):
        await client.post("/api/auth/register", json={
            "name": "Login User", "email": "login@example.com",
            "phone": "9000000003", "password": "TestPass123!", "role": "buyer"
        })
    response = await client.post("/api/auth/login", json={
        "email": "login@example.com", "password": "TestPass123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    response = await client.post("/api/auth/login", json={
        "email": "login@example.com", "password": "WrongPass!"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_verify_otp(client):
    with patch("app.services.auth_service.send_otp_msg91", new_callable=AsyncMock):
        with patch("app.services.auth_service.store_otp_redis", new_callable=AsyncMock):
            with patch("app.services.auth_service.verify_otp_redis", new_callable=AsyncMock, return_value=True):
                response = await client.post("/api/auth/verify-otp", json={
                    "phone": "9876543210", "otp": "123456"
                })
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_logout(client):
    with patch("app.services.auth_service.send_otp_msg91", new_callable=AsyncMock):
        reg = await client.post("/api/auth/register", json={
            "name": "Logout User", "email": "logout@example.com",
            "phone": "9000000004", "password": "TestPass123!", "role": "buyer"
        })
    token = reg.json()["data"]["access_token"]
    with patch("app.services.auth_service.invalidate_refresh_token", new_callable=AsyncMock):
        response = await client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
