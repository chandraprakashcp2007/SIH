"""
PRAHARI Copilot Pydantic v2 Schemas
Data contracts for chat requests, responses, tool results, streaming, and metrics.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class StructuredComponent(BaseModel):
    """Rich structured display element for frontend command centre rendering."""
    type: str  # METRIC, STATUS, ALERT_SUMMARY, NODE_SUMMARY, TABLE, TIMELINE, CHART_REQUEST, DOC_REFERENCE, ACTION_LINK
    title: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class ToolCallRecord(BaseModel):
    """Summary of a tool executed during a Copilot inquiry."""
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    latency_ms: float = 0.0
    error: Optional[str] = None


class ToolResult(BaseModel):
    """Standardized tool response contract. No unstructured raw strings internally."""
    success: bool
    tool: str
    data_mode: str = "REAL"  # REAL or SIMULATION
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data: Any = Field(default_factory=dict)
    error: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Operator inquiry text")
    session_id: Optional[str] = Field(None, description="Optional conversation session ID")
    stream: bool = Field(False, description="Whether to request SSE token stream")
    fast_path_only: bool = Field(False, description="Force deterministic local response")


class ChatResponse(BaseModel):
    request_id: str
    session_id: str
    mode: str = "LOCAL_ASSISTANT"  # ONLINE_AI, LOCAL_ASSISTANT, DEGRADED
    data_mode: str = "REAL"        # REAL, SIMULATION
    answer: str
    reply: str = ""                # Backward-compatible alias for answer
    components: List[StructuredComponent] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    tool_calls: List[ToolCallRecord] = Field(default_factory=list)
    latency_ms: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    grounded: bool = True
    provider: str = "LOCAL_DETERMINISTIC"


class StreamEvent(BaseModel):
    event: str  # status, token, source, component, error, complete
    data: Dict[str, Any]


class SessionCreate(BaseModel):
    title: Optional[str] = "Operational Inquiry"


class SessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    mode: str
    created_at: str
    updated_at: str
    message_count: int = 0


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: str
    latency_ms: float
    provider: str
    model: str
    data_mode: str
    sources: List[str] = Field(default_factory=list)
    components: List[StructuredComponent] = Field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)


class FeedbackCreate(BaseModel):
    message_id: str
    rating: str = Field(..., pattern="^(UP|DOWN)$")
    issue_type: Optional[str] = None  # Incorrect data, Too slow, Unclear, Missing information
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    status: str = "success"
    message: str = "Feedback recorded"


class CopilotHealthResponse(BaseModel):
    status: str  # healthy, degraded, unavailable
    provider: str
    mode: str
    tools_ready: int
    total_tools: int
    docs_index_ready: bool
    database_ready: bool
    last_error: Optional[str] = None
    average_latency_ms: float = 0.0


class CopilotMetricsResponse(BaseModel):
    total_requests: int
    fast_path_requests: int
    llm_path_requests: int
    offline_fallback_requests: int
    error_count: int
    timeout_count: int
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    cache_hits: int
    tool_call_counts: Dict[str, int]
