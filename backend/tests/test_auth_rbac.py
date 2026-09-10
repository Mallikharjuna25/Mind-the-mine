"""
Tests for Authentication & Role-Based Access Control (RBAC)
"""

import pytest


@pytest.mark.asyncio
async def test_user_registration_and_login(client):
    # 1. Register User
    reg_payload = {
        "email": "test_officer@mineguard.in",
        "password": "Password@123",
        "full_name": "Test Safety Officer",
        "role": "SAFETY_OFFICER",
        "designation": "Safety Lead"
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert reg_data["success"] is True
    assert reg_data["data"]["email"] == "test_officer@mineguard.in"

    # 2. Login
    login_payload = {
        "email": "test_officer@mineguard.in",
        "password": "Password@123"
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data["data"]
    token = login_data["data"]["access_token"]

    # 3. Access Protected /me Endpoint
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["data"]["role"] == "SAFETY_OFFICER"


@pytest.mark.asyncio
async def test_login_invalid_password(client):
    reg_payload = {
        "email": "valid_user@mineguard.in",
        "password": "CorrectPassword123",
        "full_name": "Valid User",
        "role": "MINE_MANAGER"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await client.post("/api/v1/auth/login", json={
        "email": "valid_user@mineguard.in",
        "password": "WrongPassword999"
    })
    assert login_res.status_code == 401
