"""
LoRa Gateway Packet Logs and Topology Database Models
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Index
from backend.app.core.database import Base


class GatewayPacketLog(Base):
    __tablename__ = "gateway_packet_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(32), nullable=False, index=True)
    sequence = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    rssi = Column(Integer, nullable=False)
    payload_size_bytes = Column(Integer, default=0)
    is_valid = Column(Boolean, default=True)
    is_duplicate = Column(Boolean, default=False)
    sequence_gap = Column(Integer, default=0)
    rejection_reason = Column(String(128), nullable=True)
    gateway_source = Column(String(32), default="USB_SERIAL")  # USB_SERIAL, SIMULATOR, MQTT
