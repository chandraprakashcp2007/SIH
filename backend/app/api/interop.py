"""Documented OGC SensorThings-compatible read-only subset."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.domain.registry import DOMAIN_REGISTRY
from backend.app.models.nodes import Node
from backend.app.models.observations import Observation


router = APIRouter(prefix="/interop/sensorthings", tags=["Interoperability"])


@router.get("/Things")
async def things(db: AsyncSession = Depends(get_db)):
    nodes = (await db.execute(select(Node).order_by(Node.id))).scalars().all()
    return {"@iot.count": len(nodes), "value": [
        {
            "@iot.id": node.id,
            "name": node.name,
            "description": DOMAIN_REGISTRY[node.id].description,
            "properties": {
                "provenance": node.source_mode,
                "hardware_state": DOMAIN_REGISTRY[node.id].hardware_state,
            },
        }
        for node in nodes
    ]}


@router.get("/Locations")
async def locations(db: AsyncSession = Depends(get_db)):
    nodes = (await db.execute(select(Node).order_by(Node.id))).scalars().all()
    return {"@iot.count": len(nodes), "value": [
        {
            "@iot.id": f"{node.id}:location",
            "name": node.location_name,
            "location": {
                "type": "Point", "coordinates": [node.longitude, node.latitude]
            },
            "properties": {"provenance": node.source_mode},
        }
        for node in nodes
    ]}


@router.get("/Sensors")
async def sensors(db: AsyncSession = Depends(get_db)):
    nodes = (await db.execute(select(Node).order_by(Node.id))).scalars().all()
    values = []
    for node in nodes:
        for metric in DOMAIN_REGISTRY[node.id].supported_metrics:
            values.append({
                "@iot.id": f"{node.id}:{metric}",
                "name": metric,
                "description": "Configured metric; availability depends on provenance.",
                "metadata": node.hardware_profile or {},
            })
    return {"@iot.count": len(values), "value": values}


@router.get("/Datastreams")
async def datastreams(db: AsyncSession = Depends(get_db)):
    result = await sensors(db)
    return {"@iot.count": result["@iot.count"], "value": [
        {
            "@iot.id": item["@iot.id"],
            "name": item["name"],
            "Thing@iot.navigationLink": item["@iot.id"].split(":", 1)[0],
            "properties": {"status": "CONFIGURED_NOT_GUARANTEED_LIVE"},
        }
        for item in result["value"]
    ]}


@router.get("/Observations")
async def observations(
    node_id: str | None = None,
    sequence_number: int | None = None,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    query = select(Observation)
    if node_id:
        query = query.where(Observation.node_id == node_id)
    if sequence_number is not None:
        query = query.where(Observation.sequence_number == sequence_number)
    records = (await db.execute(
        query.order_by(desc(Observation.timestamp)).limit(limit)
    )).scalars().all()
    value = [{
        "@iot.id": item.id,
        "node_id": item.node_id,
        "sensor_id": item.sensor_id,
        "domain": item.domain,
        "observed_property": item.observed_property,
        "value": item.value,
        "unit": item.unit,
        "timestamp": item.timestamp.isoformat(),
        "received_at": item.received_at.isoformat(),
        "latitude": item.latitude,
        "longitude": item.longitude,
        "source": item.source,
        "provenance": item.provenance,
        "quality_score": item.quality_score,
        "trust_score": item.trust_score,
        "freshness_seconds": item.freshness_seconds,
        "sequence_number": item.sequence_number,
        "firmware_version": item.firmware_version,
        "metadata": item.metadata_info,
        "raw_payload_hash": item.raw_payload_hash,
    } for item in records]
    return {"@iot.count": len(value), "value": value}
