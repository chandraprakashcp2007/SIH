"""
Risk Assessment Database Models
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, JSON, Text, Index
from backend.app.core.database import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(32), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    risk_band = Column(String(16), nullable=False)  # NORMAL, WATCH, WARNING, CRITICAL
    confidence = Column(Float, nullable=False)      # 0 - 100
    anomaly_score = Column(Float, default=0.0)      # 0.0 - 1.0
    sensor_trust = Column(JSON, default=dict)
    contributing_factors = Column(JSON, default=list)
    human_explanation = Column(Text, nullable=False)
    machine_explanation = Column(JSON, default=dict)
    recommended_action = Column(Text, nullable=False)
    model_source = Column(String(32), default="RULE_FUSION")
    estimated_crossing_time = Column(String(64), nullable=True)
    risk_trend = Column(String(32), default="STABLE")

    __table_args__ = (
        Index('idx_risk_node_time', 'node_id', 'timestamp'),
    )
