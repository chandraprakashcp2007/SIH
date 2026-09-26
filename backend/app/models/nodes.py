"""
Sensor Node Registry and Location Database Models
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, Text, JSON
from backend.app.core.database import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(String(32), primary_key=True)  # Pancha Bhootha node identifiers
    name = Column(String(64), nullable=False)
    node_type = Column(String(32), nullable=False)  # FLOOD, FIRE, LANDSLIDE, AIR_QUALITY, WEATHER, AIR_QUALITY, WEATHER
    tagline = Column(String(128), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_m = Column(Float, default=0.0)
    location_name = Column(String(128), nullable=False)
    status = Column(String(32), default="OFFLINE", nullable=False)  # ONLINE, SIMULATION, DEGRADED, MAINTENANCE, OFFLINE
    firmware_version = Column(String(32), default="v1.4.2-lora")
    hardware_rev = Column(String(32), default="SX1276-ESP32-RevB")
    battery_pct = Column(Float, default=100.0)
    solar_voltage = Column(Float, default=4.2)
    signal_rssi = Column(Integer, default=-75)
    packet_loss_pct = Column(Float, default=0.0)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    sensors_configured = Column(JSON, default=list)  # list of active sensor names
    metadata_info = Column(JSON, default=dict)
    source_mode = Column(String(32), default="SIMULATION", nullable=False, index=True)
    hardware_profile = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
