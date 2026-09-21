"""
Telemetry Records Database Models
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Index
from backend.app.core.database import Base


class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(32), nullable=False, index=True)
    sequence = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    rssi = Column(Integer, nullable=False)
    battery_pct = Column(Float, nullable=False)
    raw_payload = Column(JSON, nullable=False)  # Full JSON payload received
    metrics = Column(JSON, nullable=False)      # Specific sensor values dictionary
    is_simulation = Column(Integer, default=1)  # 1 for simulation, 0 for real LoRa hardware

    __table_args__ = (
        Index('idx_node_timestamp', 'node_id', 'timestamp'),
    )
