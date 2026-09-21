"""
PRAHARI Copilot FastAPI Router
Exposes REST and SSE endpoints for operational inquiries, sessions, feedback, and metrics.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.copilot.schemas import (
    ChatRequest,
    ChatResponse,
    SessionCreate,
    SessionResponse,
    MessageResponse,
    FeedbackCreate,
    FeedbackResponse,
    CopilotHealthResponse,
    CopilotMetricsResponse
)
from backend.app.copilot.service import copilot_service
from backend.app.copilot.orchestrator import copilot_orchestrator
from backend.app.copilot.session_store import session_store
from backend.app.core.security import decode_access_token
from backend.app.models.users import User

router = APIRouter(prefix="/copilot", tags=["PRAHARI Copilot"])


async def get_optional_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Extract username from token if present, otherwise default to 'operator'."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            return payload["sub"]
    return "operator"


@router.post("/chat", response_model=ChatResponse)
async def chat_with_copilot(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_optional_user_id)
):
    """
    Standard synchronous query endpoint.
    Executes fast-path or LLM with full grounding and returns structured cards.
    """
    return await copilot_service.chat(db, req, user_id=user_id)


@router.get("/stream")
async def stream_copilot_chat(
    query: str = Query(..., min_length=1, max_length=2000, description="Operator inquiry text"),
    session_id: Optional[str] = Query(None, description="Optional conversation session ID"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_optional_user_id)
):
    """
    Server-Sent Events (SSE) real-time streaming endpoint.
    Yields operational status updates, response tokens, source chips, and structured cards.
    """
    generator = copilot_orchestrator.stream_query(
        db=db,
        query=query,
        session_id=session_id,
        user_id=user_id
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/health", response_model=CopilotHealthResponse)
async def get_copilot_health():
    """Liveness, readiness, tool status, and index state diagnostic check."""
    return await copilot_service.get_health()


@router.get("/metrics", response_model=CopilotMetricsResponse)
async def get_copilot_metrics():
    """Observability endpoint returning latency percentiles (p50, p95, p99) and counters."""
    return await copilot_service.get_metrics()


@router.get("/suggestions", response_model=List[str])
async def get_suggested_questions():
    """Retrieve pre-calibrated operational prompt suggestions."""
    return await copilot_service.get_suggestions()


@router.get("/sessions", response_model=List[SessionResponse])
async def list_chat_sessions(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_optional_user_id)
):
    """List recent conversation sessions for the current operator."""
    return await session_store.list_sessions(db, user_id=user_id, limit=limit)


@router.post("/sessions", response_model=SessionResponse)
async def create_chat_session(
    body: SessionCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_optional_user_id)
):
    """Start a new clean chat session."""
    sess = await session_store.get_or_create_session(db, user_id=user_id, title=body.title or "New Inquiry")
    return SessionResponse(
        id=sess.id,
        user_id=sess.user_id,
        title=sess.title,
        mode=sess.mode,
        created_at=sess.created_at.isoformat(),
        updated_at=sess.updated_at.isoformat(),
        message_count=0
    )


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_optional_user_id),
):
    """Delete a conversation session and its message logs."""
    deleted = await session_store.delete_session(db, session_id=session_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"status": "success", "session_id": session_id}


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_optional_user_id),
):
    """Retrieve dialogue history for a session."""
    return await session_store.get_messages(db, session_id=session_id, limit=limit, user_id=user_id)


@router.post("/feedback", response_model=FeedbackResponse)
async def record_copilot_feedback(
    fb: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_optional_user_id)
):
    """Submit operator feedback (thumbs up / down) on Copilot answers."""
    return await copilot_service.record_feedback(db, fb, user_id=user_id)
