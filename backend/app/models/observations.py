"""Canonical, provenance-preserving sensor observations."""
import uuid

from sqlalchemy import DateTime, Float, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    node_id: Mapped[str] = mapped_column(String(32), index=True)
    sensor_id: Mapped[str] = mapped_column(String(96), index=True)
    domain: Mapped[str] = mapped_column(String(16), index=True)
    observed_property: Mapped[str] = mapped_column(String(96), index=True)
    value: Mapped[object] = mapped_column(JSON)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    timestamp: Mapped[object] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[object] = mapped_column(DateTime(timezone=True), index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(64))
    provenance: Mapped[str] = mapped_column(String(32), index=True)
    quality_score: Mapped[float] = mapped_column(Float)
    trust_score: Mapped[float] = mapped_column(Float)
    freshness_seconds: Mapped[float] = mapped_column(Float)
    sequence_number: Mapped[int] = mapped_column(Integer, index=True)
    firmware_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_info: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    raw_payload_hash: Mapped[str] = mapped_column(String(64), index=True)

    __table_args__ = (
        Index("idx_observation_node_time", "node_id", "timestamp"),
        Index("idx_observation_domain_time", "domain", "timestamp"),
    )
