"""
PRAHARI Copilot Application Service
Provides high-level session, metrics, suggestion, and health query services.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.copilot.schemas import (
    ChatRequest,
    ChatResponse,
    FeedbackCreate,
    FeedbackResponse,
    CopilotHealthResponse,
    CopilotMetricsResponse
)
from backend.app.copilot.orchestrator import copilot_orchestrator
from backend.app.copilot.session_store import session_store
from backend.app.copilot.metrics import copilot_metrics
from backend.app.copilot.cache import copilot_cache
from backend.app.copilot.tool_registry import tool_registry
from backend.app.copilot.retrieval import knowledge_retriever
from backend.app.core.config import settings
from gateway.simulator import prahari_sim

SUGGESTED_PROMPTS = [
    "Why is JALA-01 critical?",
    "Which node currently has the highest risk?",
    "Explain the latest alert.",
    "Show unacknowledged alerts.",
    "Which sensor currently has low trust?",
    "Check gateway health.",
    "Which node has weakest RSSI?",
    "Explain why AGNI-02 generated this fire alert.",
    "Show the last 10 minutes of JALA water trend.",
    "What happened during EVT-001?",
    "Is PRAHARI running offline?",
    "Explain multi-sensor fusion.",
    "Explain sensor trust.",
    "Show current system health.",
    "What changed in the last 5 minutes?",
    "Compare JALA and BHUMI risk.",
    "Which devices need maintenance?"
]


class CopilotService:
    """Coordinates business logic across Copilot components."""

    async def prewarm(self):
        """Pre-warm in-memory indices and cache on backend startup."""
        try:
            knowledge_retriever.build_index()
        except Exception:
            pass

    async def chat(self, db: AsyncSession, req: ChatRequest, user_id: str = "operator") -> ChatResponse:
        return await copilot_orchestrator.handle_query(db, req, user_id=user_id)

    async def get_health(self) -> CopilotHealthResponse:
        if not knowledge_retriever.is_ready:
            knowledge_retriever.build_index()
        stats = copilot_metrics.get_summary()
        tools_count = len(tool_registry.list_tool_names())
        mode_str = "ONLINE_AI" if (copilot_orchestrator.online_provider and copilot_orchestrator.online_provider.is_configured()) else "LOCAL_ASSISTANT"

        return CopilotHealthResponse(
            status="healthy",
            provider=settings.LLM_PROVIDER,
            mode=mode_str,
            tools_ready=tools_count,
            total_tools=tools_count,
            docs_index_ready=knowledge_retriever.is_ready,
            database_ready=True,
            last_error=None,
            average_latency_ms=stats.get("avg_latency_ms", 0.0)
        )

    async def get_metrics(self) -> CopilotMetricsResponse:
        stats = copilot_metrics.get_summary(cache_hits=copilot_cache.hits)
        return CopilotMetricsResponse(**stats)

    async def get_suggestions(self) -> List[str]:
        return SUGGESTED_PROMPTS

    async def record_feedback(self, db: AsyncSession, fb: FeedbackCreate, user_id: str = "operator") -> FeedbackResponse:
        res = await session_store.record_feedback(
            db=db,
            message_id=fb.message_id,
            user_id=user_id,
            rating=fb.rating,
            issue_type=fb.issue_type,
            comment=fb.comment
        )
        return FeedbackResponse(id=res.id, status="success", message="Feedback recorded.")


copilot_service = CopilotService()
