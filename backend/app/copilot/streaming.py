"""
PRAHARI Copilot Server-Sent Events (SSE) Streaming Generator
Emits operational status, tokens, source chips, and structured cards in real time.
"""
import json
import asyncio
from typing import AsyncGenerator, Dict, Any, List
from backend.app.copilot.schemas import StructuredComponent


def format_sse(event_type: str, data: Dict[str, Any]) -> str:
    """Format an SSE message."""
    json_str = json.dumps(data)
    return f"event: {event_type}\ndata: {json_str}\n\n"


async def stream_copilot_response(
    status_steps: List[str],
    token_chunks: List[str],
    sources: List[str],
    components: List[StructuredComponent],
    latency_ms: float,
    request_id: str,
    session_id: str,
    mode: str = "LOCAL_ASSISTANT",
    data_mode: str = "REAL"
) -> AsyncGenerator[str, None]:
    """Generates a complete SSE stream for chat clients."""
    # 1. Operational status steps
    for step in status_steps:
        yield format_sse("status", {"message": step, "request_id": request_id})
        await asyncio.sleep(0.03)

    # 2. Source chips
    for src in sources:
        yield format_sse("source", {"source": src, "request_id": request_id})

    # 3. Stream visible answer tokens
    for chunk in token_chunks:
        yield format_sse("token", {"text": chunk, "request_id": request_id})
        await asyncio.sleep(0.01)

    # 4. Structured UI components
    for comp in components:
        yield format_sse("component", comp.model_dump())

    # 5. Stream complete event
    yield format_sse("complete", {
        "request_id": request_id,
        "session_id": session_id,
        "latency_ms": latency_ms,
        "mode": mode,
        "data_mode": data_mode
    })
