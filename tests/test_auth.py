"""
Authentication and Cryptographic Unit Tests
"""
import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from backend.app.main import authenticate_websocket_token


def test_password_hashing_and_verification():
    secret = "StrongPrahariPassword123!"
    hashed = hash_password(secret)

    assert hashed.startswith("pbkdf2_sha256$")
    assert verify_password(secret, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_generation_and_decoding():
    payload = {"sub": "operator", "role": "OPERATOR"}
    token = create_access_token(payload, expires_delta_seconds=60)

    assert isinstance(token, str)
    assert len(token.split('.')) == 3

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "operator"
    assert decoded["role"] == "OPERATOR"


def test_jwt_tampered_token_rejected():
    token = create_access_token({"sub": "viewer"}, expires_delta_seconds=60)
    # Tamper with signature
    parts = token.split('.')
    tampered = f"{parts[0]}.{parts[1]}.bad_signature"
    assert decode_access_token(tampered) is None


@pytest.mark.asyncio
async def test_dev_auth_bypass_accepts_any_non_empty_credentials(monkeypatch):
    monkeypatch.setattr(settings, "DEV_AUTH_BYPASS", True)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/auth/login", json={"username": "judge", "password": "local-demo"})
    assert response.status_code == 200
    assert response.json()["user"]["dev_auth_bypass"] is True


@pytest.mark.asyncio
async def test_dev_auth_bypass_rejects_empty_credentials(monkeypatch):
    monkeypatch.setattr(settings, "DEV_AUTH_BYPASS", True)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/auth/login", json={"username": " ", "password": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_protected_endpoint_rejects_anonymous_request():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/nodes")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_viewer_cannot_trigger_simulator():
    token = create_access_token({"sub": "viewer", "role": "VIEWER"})
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/simulator/scenario/ALL_NORMAL", headers=headers)
    assert response.status_code == 403


def test_websocket_token_validation_rejects_missing_or_tampered_token():
    assert authenticate_websocket_token(None) is None
    assert authenticate_websocket_token("tampered") is None


def test_websocket_token_validation_accepts_signed_token():
    token = create_access_token({"sub": "operator", "role": "OPERATOR"})
    assert authenticate_websocket_token(token)["sub"] == "operator"
