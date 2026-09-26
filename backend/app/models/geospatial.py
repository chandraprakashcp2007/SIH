"""Geospatial dataset registry and GeoJSON feature storage."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Index, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class GeoDataset(Base):
    __tablename__ = "geo_datasets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    domain: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(256))
    provider: Mapped[str] = mapped_column(String(128))
    version: Mapped[str] = mapped_column(String(64))
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_time: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    spatial_extent: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    temporal_extent: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    license_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provenance: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    metadata_info: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class GeoFeature(Base):
    __tablename__ = "geo_features"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id: Mapped[str] = mapped_column(String(64), index=True)
    domain: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    feature_type: Mapped[str] = mapped_column(String(64), index=True)
    geometry: Mapped[dict] = mapped_column(JSON)
    properties: Mapped[dict] = mapped_column(JSON, default=dict)
    min_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    provenance: Mapped[str] = mapped_column(String(32), index=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_geo_feature_domain_type", "domain", "feature_type"),
    )
