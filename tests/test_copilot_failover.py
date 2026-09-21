"""
Tests for Copilot Model Provider Failover & Offline Degradation
"""
import pytest
import pytest_asyncio
from backend.app.core.database import AsyncSessionLocal
from backend.app.copilot.orchestrator import copilot_orchestrator
from backend.app.copilot.providers.mock_adapter import MockProvider
from backend.app.copilot.schemas import ChatRequest


@pytest.mark.asyncio
async def test_provider_failover_to_local_assistant():
    """Verify that when an external LLM fails, Copilot gracefully degrades to Local Assistant."""
    # Attach a failing mock provider
    failing_provider = MockProvider()
    failing_provider.should_fail = True
    original_provider = copilot_orchestrator.online_provider

    try:
        copilot_orchestrator.online_provider = failing_provider

        async with AsyncSessionLocal() as db:
            req = ChatRequest(message="How does PRAHARI work?", fast_path_only=False)
            resp = await copilot_orchestrator.handle_query(db, req)
            # Response must NOT crash; must degrade to LOCAL_ASSISTANT
            assert resp.mode == "LOCAL_ASSISTANT"
            assert resp.provider == "LOCAL_DETERMINISTIC"
            assert len(resp.answer) > 10

    finally:
        copilot_orchestrator.online_provider = original_provider
