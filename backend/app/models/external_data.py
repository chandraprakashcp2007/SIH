"""
PRAHARI-NET Authoritative External Data Persistence
External observations are NEVER physical REAL node telemetry.
"""
from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text

from backend.app.core.database import Base


class ExternalObservation(Base):
    __tablename__ = "external_observations"

    id = Column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    provider = Column(String(64), nullable=False, index=True)
    dataset = Column(String(128), nullable=False, index=True)
    product = Column(String(128), nullable=True)

    retrieved_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    observation_time = Column(DateTime, nullable=False, index=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    region = Column(String(256), nullable=True)

    parameter = Column(String(128), nullable=False, index=True)

    raw_value = Column(JSON, nullable=False)
    normalized_value = Column(Float, nullable=True)
    unit = Column(String(64), nullable=True)

    freshness_seconds = Column(Integer, nullable=True)
    quality_flags = Column(JSON, default=list, nullable=False)

    source_identifier = Column(String(512), nullable=True)
    source_url = Column(Text, nullable=True)
    access_note = Column(Text, nullable=True)

    checksum = Column(String(128), nullable=True)

    provenance = Column(
        String(32),
        nullable=False,
        default="EXTERNAL_DATA",
        index=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ExternalProviderState(Base):
    __tablename__ = "external_provider_states"

    provider = Column(String(64), primary_key=True)

    state = Column(
        String(32),
        nullable=False,
        default="NOT_CONFIGURED",
        index=True,
    )

    last_attempt_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)

    last_error = Column(Text, nullable=True)
    access_note = Column(Text, nullable=True)

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
