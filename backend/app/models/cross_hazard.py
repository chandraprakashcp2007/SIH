"""Persisted cross-hazard, compound-risk, and peer-consensus assessments."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


def _id() -> str:
    return str(uuid.uuid4())


class CrossHazardRelationship(Base):
    __tablename__ = "cross_hazard_relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    source_node_id: Mapped[str] = mapped_column(String(32), index=True)
    target_node_id: Mapped[str] = mapped_column(String(32), index=True)
    relationship_type: Mapped[str] = mapped_column(String(40), default="CONFIGURED_RELATIONSHIP")
    state: Mapped[str] = mapped_column(String(24), index=True)
    source_risk_band: Mapped[str] = mapped_column(String(16))
    target_risk_band: Mapped[str] = mapped_column(String(16))
    confidence: Mapped[float] = mapped_column(Float)
    provenance: Mapped[str] = mapped_column(String(32), index=True)
    evidence_refs: Mapped[list] = mapped_column(JSON, default=list)
    explanation: Mapped[str] = mapped_column(Text)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class CompoundRiskAssessment(Base):
    __tablename__ = "compound_risk_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    rule_id: Mapped[str] = mapped_column(String(64), index=True)
    rule_version: Mapped[str] = mapped_column(String(16))
    participants: Mapped[list] = mapped_column(JSON)
    risk_class: Mapped[str] = mapped_column(String(24), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    uncertainty: Mapped[float] = mapped_column(Float)
    provenance: Mapped[str] = mapped_column(String(32), index=True)
    method: Mapped[str] = mapped_column(String(32), default="TRANSPARENT_RULE")
    evidence_refs: Mapped[list] = mapped_column(JSON, default=list)
    explanation: Mapped[str] = mapped_column(Text)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class ConsensusAssessment(Base):
    __tablename__ = "consensus_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    node_id: Mapped[str] = mapped_column(String(32), index=True)
    state: Mapped[str] = mapped_column(String(32), index=True)
    neighbour_count: Mapped[int] = mapped_column(default=0)
    required_neighbours: Mapped[int] = mapped_column(default=2)
    weights: Mapped[dict] = mapped_column(JSON, default=dict)
    provenance: Mapped[str] = mapped_column(String(32), index=True)
    explanation: Mapped[str] = mapped_column(Text)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
