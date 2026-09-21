"""
Tests for Copilot Deterministic Fast-Path
"""
import pytest
import pytest_asyncio
from backend.app.core.database import AsyncSessionLocal
from backend.app.copilot.orchestrator import copilot_orchestrator
from backend.app.copilot.schemas import ChatRequest


@pytest.mark.asyncio
async def test_fast_path_highest_risk():
    async with AsyncSessionLocal() as db:
        req = ChatRequest(message="Which node currently has the highest risk?")
        resp = await copilot_orchestrator.handle_query(db, req)
        assert resp.mode == "LOCAL_ASSISTANT"
        assert resp.grounded is True
        assert len(resp.sources) > 0
        assert "risk score" in resp.answer.lower()
        assert len(resp.components) > 0


@pytest.mark.asyncio
async def test_fast_path_why_jala():
    async with AsyncSessionLocal() as db:
        req = ChatRequest(message="Why is JALA critical?")
        resp = await copilot_orchestrator.handle_query(db, req)
        assert "JALA-01" in resp.answer
        assert "hazard score" in resp.answer.lower() or "risk" in resp.answer.lower()
        assert resp.latency_ms < 500.0  # Fast deterministic path


@pytest.mark.asyncio
async def test_fast_path_gateway_status():
    async with AsyncSessionLocal() as db:
        req = ChatRequest(message="Is the gateway connected?")
        resp = await copilot_orchestrator.handle_query(db, req)
        assert "gateway" in resp.answer.lower()
        assert "connected" in resp.answer.lower()


@pytest.mark.asyncio
async def test_fast_path_compare_nodes():
    async with AsyncSessionLocal() as db:
        req = ChatRequest(message="Compare JALA and BHUMI risk.")
        resp = await copilot_orchestrator.handle_query(db, req)
        assert "JALA-01" in resp.answer
        assert "BHUMI-03" in resp.answer
        # Check structured table component
        has_table = any(c.type == "TABLE" for c in resp.components)
        assert has_table is True
