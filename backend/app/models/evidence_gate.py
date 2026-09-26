import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class EvidenceItem(Base):
    __tablename__ = "evidence_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hazard: Mapped[str] = mapped_column(String(32), index=True)
    source: Mapped[str] = mapped_column(String(128))
    provider: Mapped[str] = mapped_column(String(128))
    provenance: Mapped[str] = mapped_column(String(32), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    freshness_seconds: Mapped[float] = mapped_column(Float)
    quality: Mapped[float] = mapped_column(Float)
    trust: Mapped[float] = mapped_column(Float)
    spatial_relevance: Mapped[float] = mapped_column(Float)
    temporal_relevance: Mapped[float] = mapped_column(Float)
    claim: Mapped[dict] = mapped_column(JSON)
    metadata_info: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class EvidenceGateEvaluation(Base):
    __tablename__ = "evidence_gate_evaluations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hazard: Mapped[str] = mapped_column(String(32), index=True)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    lifecycle: Mapped[str] = mapped_column(String(32), index=True)
    publication_allowed: Mapped[bool] = mapped_column(Boolean)
    confidence: Mapped[float] = mapped_column(Float)
    policy_version: Mapped[str] = mapped_column(String(32))
    checks: Mapped[list] = mapped_column(JSON)
    evidence_ids: Mapped[list] = mapped_column(JSON)
    why_withheld: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
