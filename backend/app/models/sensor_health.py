"""Persisted sensor-health snapshots used by risk and fleet views."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class SensorHealthSnapshot(Base):
    __tablename__ = "sensor_health_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id: Mapped[str] = mapped_column(String(32), index=True)
    sensor_id: Mapped[str] = mapped_column(String(96), index=True)
    state: Mapped[str] = mapped_column(String(32), index=True)
    trust_score: Mapped[float] = mapped_column(Float)
    noise_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    drift_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    missing_data_pct: Mapped[float] = mapped_column(Float, default=0)
    battery_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    rssi: Mapped[int | None] = mapped_column(Integer, nullable=True)
    calibration_state: Mapped[str] = mapped_column(String(32), default="NOT_CONFIGURED")
    firmware_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    provenance: Mapped[str] = mapped_column(String(32), index=True)
    reason_codes: Mapped[list] = mapped_column(JSON, default=list)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (Index("idx_health_sensor_time", "sensor_id", "recorded_at"),)
