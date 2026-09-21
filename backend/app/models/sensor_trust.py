"""
Sensor Trust History Database Model
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, JSON, Text, Index
from backend.app.core.database import Base


class SensorTrustLog(Base):
    __tablename__ = "sensor_trust_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(32), nullable=False, index=True)
    sensor_name = Column(String(64), nullable=False, index=True)
    trust_score = Column(Float, nullable=False)  # 0 - 100
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    anomaly_detected = Column(String(64), nullable=True)  # STUCK_READING, IMPOSSIBLE_JUMP, SENSOR_CONTRADICTION, NOISE
    details = Column(JSON, default=dict)
