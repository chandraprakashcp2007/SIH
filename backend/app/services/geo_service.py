"""Backend-derived map read models with truthful layer availability."""
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.registry import DOMAIN_REGISTRY
from backend.app.models.geospatial import GeoDataset, GeoFeature
from backend.app.models.nodes import Node
from backend.app.models.risk import RiskAssessment
from backend.app.models.telemetry import TelemetryRecord


NODE_BY_DOMAIN = {item.display_name: node_id for node_id, item in DOMAIN_REGISTRY.items()}

DATASET_DEFAULTS = (
    dict(id="PRAHARI_NODES", name="PRAHARI node locations", domain=None,
         source="PRAHARI node registry", provider="PRAHARI-NET", version="1",
         provenance="REAL", status="AVAILABLE", checksum="DATABASE_DERIVED"),
    dict(id="NASA_FIRMS", name="NASA FIRMS active fire", domain="AGNI",
         source="NASA FIRMS adapter", provider="NASA", version="unconfigured",
         provenance="EXTERNAL_DATA", status="NOT_CONFIGURED", checksum=None),
    dict(id="DEM_TERRAIN", name="Digital elevation model", domain="BHUMI",
         source="Terrain dataset registry", provider="NOT_CONFIGURED", version="unconfigured",
         provenance="EXTERNAL_DATA", status="NOT_CONFIGURED", checksum=None),
    dict(id="HYDROLOGY", name="River and watershed data", domain="JALA",
         source="Hydrology dataset registry", provider="NOT_CONFIGURED", version="unconfigured",
         provenance="EXTERNAL_DATA", status="NOT_CONFIGURED", checksum=None),
    dict(id="WEATHER", name="Authoritative weather layers", domain="AKASHA",
         source="Weather provider registry", provider="NOT_CONFIGURED", version="unconfigured",
         provenance="EXTERNAL_DATA", status="NOT_CONFIGURED", checksum=None),
)

DOMAIN_LAYERS = {
    "JALA": ("river_geometry", "watershed", "water_level", "rainfall", "historical_flood", "forecast", "uncertainty", "roads", "bridges", "shelters"),
    "AGNI": ("temperature", "smoke_gas", "fire_events", "satellite_fire", "wind", "observed_hazard", "model_spread", "uncertainty", "safe_routes"),
    "BHUMI": ("dem", "elevation", "slope", "soil_moisture", "tilt", "vibration", "rain_accumulation", "susceptibility", "historical_landslides", "uncertainty"),
    "VAYU": ("gas_smoke", "pm2_5", "pm10", "temperature_humidity", "plume", "air_risk_zones", "industrial_facilities"),
    "AKASHA": ("rainfall", "pressure", "temperature", "humidity", "wind", "weather_warnings", "radar_satellite", "storm_risk"),
}


class GeoService:
    async def ensure_registry(self, db: AsyncSession) -> None:
        for data in DATASET_DEFAULTS:
            if await db.get(GeoDataset, data["id"]) is None:
                db.add(GeoDataset(
                    **data, retrieved_at=None, valid_time=None,
                    spatial_extent=None, temporal_extent=None,
                    license_reference=None, metadata_info={"stac_compatible": False},
                ))
        await db.commit()

    async def datasets(self, db: AsyncSession) -> list[GeoDataset]:
        await self.ensure_registry(db)
        return list((await db.execute(select(GeoDataset).order_by(GeoDataset.id))).scalars())

    async def domain_map(self, db: AsyncSession, domain: str) -> dict:
        domain = domain.upper()
        node_id = NODE_BY_DOMAIN.get(domain)
        if not node_id:
            raise KeyError(domain)
        await self.ensure_registry(db)
        node = await db.get(Node, node_id)
        telemetry = (await db.execute(
            select(TelemetryRecord).where(TelemetryRecord.node_id == node_id)
            .order_by(desc(TelemetryRecord.server_received_at)).limit(1)
        )).scalar_one_or_none()
        risk = (await db.execute(
            select(RiskAssessment).where(RiskAssessment.node_id == node_id)
            .order_by(desc(RiskAssessment.timestamp)).limit(1)
        )).scalar_one_or_none()
        risk_band = {"NORMAL": "SAFE"}.get(risk.risk_band, risk.risk_band) if risk else "NO_DATA"
        now = datetime.now(timezone.utc)
        freshness = None
        if telemetry:
            received = telemetry.server_received_at
            if received.tzinfo is None:
                received = received.replace(tzinfo=timezone.utc)
            freshness = max(0, int((now - received).total_seconds()))
        configured_metrics = set(DOMAIN_REGISTRY[node_id].supported_metrics)
        observed_metrics = set((telemetry.metrics if telemetry else {}).keys())
        layers = []
        for layer in DOMAIN_LAYERS[domain]:
            status = "NOT_CONFIGURED"
            if layer in {"water_level", "rainfall", "temperature", "soil_moisture", "tilt", "vibration", "pressure", "humidity", "wind", "gas_smoke", "smoke_gas", "pm2_5", "pm10"}:
                tokens = layer.split("_")
                supported = any(any(token in metric for token in tokens) for metric in configured_metrics)
                observed = any(any(token in metric for token in tokens) for metric in observed_metrics)
                status = "AVAILABLE" if observed else ("NO_LIVE_DATA" if supported else "NOT_CONFIGURED")
            if layer in {"forecast", "model_spread", "susceptibility", "plume", "uncertainty"}:
                status = "PLANNED"
            layers.append({"id": layer, "status": status, "provenance": telemetry.source_mode if telemetry and status == "AVAILABLE" else "PLANNED" if status == "PLANNED" else "EXTERNAL_DATA"})
        feature = {
            "type": "Feature", "id": node.id,
            "geometry": {"type": "Point", "coordinates": [node.longitude, node.latitude]},
            "properties": {
                "node_id": node.id, "name": node.name,
                "risk_band": risk_band, "risk_score": risk.risk_score if risk else None,
                "confidence": risk.confidence if risk else None,
                "provenance": telemetry.source_mode if telemetry else node.source_mode,
                "observed_at": telemetry.device_timestamp.isoformat() if telemetry else None,
                "received_at": telemetry.server_received_at.isoformat() if telemetry else None,
                "freshness_seconds": freshness,
                "metrics": telemetry.metrics if telemetry else {},
                "location_name": node.location_name,
            },
        }
        return {"type": "FeatureCollection", "domain": domain, "generated_at": now.isoformat(), "features": [feature], "layers": layers}


geo_service = GeoService()
