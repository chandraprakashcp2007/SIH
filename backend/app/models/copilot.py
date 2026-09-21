"""
PRAHARI-NET Copilot Database Models
Manages chat sessions, messages, tool execution logs, operator feedback, and system metrics.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text, Index, ForeignKey
from backend.app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), nullable=False, default="operator", index=True)
    title = Column(String(256), nullable=False, default="Operational Inquiry")
    mode = Column(String(32), default="LOCAL_ASSISTANT", nullable=False)  # ONLINE_AI, LOCAL_ASSISTANT, DEGRADED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_chat_session_user_updated", "user_id", "updated_at"),
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(16), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    latency_ms = Column(Float, default=0.0)
    provider = Column(String(64), default="LOCAL_DETERMINISTIC")
    model = Column(String(64), default="local-expert-v1")
    data_mode = Column(String(16), default="REAL")  # REAL, SIMULATION
    sources = Column(JSON, default=list)            # ["LIVE_TELEMETRY", "RISK_ENGINE"]
    components = Column(JSON, default=list)         # Structured cards payload
    tool_calls = Column(JSON, default=list)         # Summary of tool calls made

    __table_args__ = (
        Index("idx_chat_messages_session_time", "session_id", "created_at"),
    )


class CopilotToolCall(Base):
    __tablename__ = "copilot_tool_calls"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), nullable=True, index=True)
    session_id = Column(String(36), nullable=True, index=True)
    tool_name = Column(String(64), nullable=False, index=True)
    request_json = Column(JSON, default=dict)
    response_summary = Column(Text, nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)


class CopilotFeedback(Base):
    __tablename__ = "copilot_feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(64), default="operator")
    rating = Column(String(16), nullable=False)  # UP, DOWN
    issue_type = Column(String(64), nullable=True)  # Incorrect data, Too slow, Unclear, Missing information
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class CopilotMetric(Base):
    __tablename__ = "copilot_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(64), nullable=False, index=True)
    value = Column(Float, nullable=False)
    dimensions = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
