"""
Tests for Copilot API Endpoints, Sessions, Feedback, and Anti-Hallucination
"""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.security import create_access_token

AUTH_HEADERS = {"Authorization": f"Bearer {create_access_token({'sub': 'operator', 'role': 'OPERATOR', 'dev_auth_bypass': True})}"}


@pytest.mark.asyncio
async def test_copilot_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/copilot/health", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["tools_ready"] >= 20
        assert data["docs_index_ready"] is True


@pytest.mark.asyncio
async def test_copilot_metrics_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/copilot/metrics", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_requests" in data
        assert "p50_latency_ms" in data


@pytest.mark.asyncio
async def test_copilot_suggestions_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/copilot/suggestions", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 5


@pytest.mark.asyncio
async def test_copilot_session_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create session
        c_resp = await ac.post("/api/copilot/sessions", json={"title": "Test Session"}, headers=AUTH_HEADERS)
        assert c_resp.status_code == 200
        sess = c_resp.json()
        sess_id = sess["id"]

        # List sessions
        l_resp = await ac.get("/api/copilot/sessions", headers=AUTH_HEADERS)
        assert l_resp.status_code == 200
        assert any(s["id"] == sess_id for s in l_resp.json())

        # Delete session
        d_resp = await ac.delete(f"/api/copilot/sessions/{sess_id}", headers=AUTH_HEADERS)
        assert d_resp.status_code == 200


@pytest.mark.asyncio
async def test_anti_hallucination_nonexistent_node():
    """Asking about a nonexistent node like JALA-99 must return not found, never hallucinate."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/copilot/chat", json={"message": "What is the status of node JALA-99?"}, headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        # Must report not found or nominal, never hallucinate false sensor values
        answer = data["answer"].lower()
        assert "not found" in answer or "unavailable" in answer or "unknown" in answer
