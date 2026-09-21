"""
Alert and Incident Lifecycle Database Models
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, JSON, Text, Index
from backend.app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: f"ALT-{uuid.uuid4().hex[:8].upper()}")
    severity = Column(String(16), nullable=False)  # WATCH, WARNING, CRITICAL
    hazard = Column(String(32), nullable=False)    # FLOOD, FIRE, LANDSLIDE
    node_id = Column(String(32), nullable=False, index=True)
    location_name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(64), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(64), nullable=True)
    state = Column(String(16), default="NEW", nullable=False, index=True)  # NEW, ACKNOWLEDGED, MONITORING, RESOLVED
    confidence = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    headline = Column(String(256), nullable=False)
    summary = Column(Text, nullable=False)
    action_recommended = Column(Text, nullable=False)
    evidence = Column(JSON, default=dict)
    resolution_notes = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_alert_state_created', 'state', 'created_at'),
    )
