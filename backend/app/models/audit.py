"""
Audit Logs and System Settings Database Models
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text, Index
from backend.app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, default="SYSTEM")
    username = Column(String(64), nullable=False, default="system")
    action = Column(String(64), nullable=False, index=True)  # LOGIN, ALERT_ACK, ALERT_RESOLVE, SIM_START, SETTING_CHANGE
    category = Column(String(32), default="OPERATIONAL")    # AUTH, AUDIT, ALERT, SETTINGS, SIMULATOR
    component = Column(String(64), default="backend")
    message = Column(Text, nullable=False)
    details = Column(JSON, default=dict)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(64), primary_key=True)
    category = Column(String(32), nullable=False)  # GENERAL, THRESHOLDS, GATEWAY, AI, AUDIO
    value_json = Column(JSON, nullable=False)
    description = Column(String(256), nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by = Column(String(64), default="system")
