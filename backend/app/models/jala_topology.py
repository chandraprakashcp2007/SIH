"""JALA river-network configuration and derived downstream threat records."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class RiverTopologyDataset(Base):
    __tablename__ = "river_topology_datasets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120))
    version: Mapped[str] = mapped_column(String(32))
    provenance: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reaches: Mapped[list] = mapped_column(JSON, default=list)
    validation: Mapped[dict] = mapped_column(JSON, default=dict)
    imported_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class DownstreamThreatAssessment(Base):
    __tablename__ = "downstream_threat_assessments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_node_id: Mapped[str] = mapped_column(String(32), index=True)
    topology_dataset_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    threatened_reaches: Mapped[list] = mapped_column(JSON, default=list)
    travel_time_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_to_impact_state: Mapped[str] = mapped_column(String(32))
    method: Mapped[str] = mapped_column(String(64))
    provenance: Mapped[str] = mapped_column(String(32), index=True)
    reason: Mapped[str] = mapped_column(Text)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
