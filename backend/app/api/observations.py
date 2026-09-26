from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.observations import Observation
from backend.app.models.sensor_health import SensorHealthSnapshot


router = APIRouter(tags=["Observations and Sensor Health"])
RANGES = {"15m": (timedelta(minutes=15), 60), "1h": (timedelta(hours=1), 300), "6h": (timedelta(hours=6), 1800), "24h": (timedelta(days=1), 7200), "7d": (timedelta(days=7), 43200)}


@router.get("/observations/aggregate")
async def aggregate_observations(
    node_id: str, observed_property: str,
    range: str = Query("1h", pattern="^(15m|1h|6h|24h|7d)$"),
    db: AsyncSession = Depends(get_db),
):
    duration, bucket_seconds = RANGES[range]
    since = datetime.now(timezone.utc) - duration
    records = list((await db.execute(
        select(Observation).where(
            Observation.node_id == node_id,
            Observation.observed_property == observed_property,
            Observation.timestamp >= since,
        ).order_by(Observation.timestamp)
    )).scalars())
    buckets: dict[int, list[Observation]] = {}
    for item in records:
        stamp = item.timestamp.replace(tzinfo=timezone.utc) if item.timestamp.tzinfo is None else item.timestamp
        key = int(stamp.timestamp()) // bucket_seconds * bucket_seconds
        buckets.setdefault(key, []).append(item)
    points = []
    for key, items in sorted(buckets.items()):
        numeric = [float(item.value) for item in items if isinstance(item.value, (int, float)) and not isinstance(item.value, bool)]
        if numeric:
            points.append({"timestamp": datetime.fromtimestamp(key, timezone.utc).isoformat(), "min": min(numeric), "max": max(numeric), "average": sum(numeric) / len(numeric), "count": len(numeric)})
    latest = records[-1] if records else None
    return {"node_id": node_id, "observed_property": observed_property, "range": range,
            "unit": latest.unit if latest else None, "source": "DATABASE_OBSERVATIONS",
            "provenance": latest.provenance if latest else "NO_DATA", "points": points}


@router.get("/sensor-health")
async def fleet_health(node_id: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(SensorHealthSnapshot)
    if node_id:
        query = query.where(SensorHealthSnapshot.node_id == node_id)
    records = list((await db.execute(query.order_by(desc(SensorHealthSnapshot.recorded_at)))).scalars())
    latest: dict[str, SensorHealthSnapshot] = {}
    for item in records:
        latest.setdefault(item.sensor_id, item)
    return [{
        "id": item.id, "node_id": item.node_id, "sensor_id": item.sensor_id,
        "state": item.state, "trust_score": item.trust_score,
        "noise_score": item.noise_score, "drift_score": item.drift_score,
        "missing_data_pct": item.missing_data_pct, "battery_pct": item.battery_pct,
        "rssi": item.rssi, "calibration_state": item.calibration_state,
        "firmware_version": item.firmware_version, "provenance": item.provenance,
        "reason_codes": item.reason_codes, "recorded_at": item.recorded_at,
    } for item in latest.values()]
