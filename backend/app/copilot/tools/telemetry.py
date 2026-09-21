"""
Copilot Telemetry Query Tools
Fetches latest packet frames and statistical range summaries.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.telemetry import TelemetryRecord
from backend.app.copilot.context_builder import summarize_telemetry_range


async def get_latest_telemetry(db: AsyncSession, node_id: str) -> Dict[str, Any]:
    """Retrieve the most recent telemetry readings for a specific node."""
    query = (
        select(TelemetryRecord)
        .where(TelemetryRecord.node_id == node_id)
        .order_by(desc(TelemetryRecord.timestamp))
        .limit(1)
    )
    res = await db.execute(query)
    record = res.scalar_one_or_none()
    if not record:
        return {"error": f"No telemetry records available for node {node_id}."}

    return {
        "node_id": record.node_id,
        "sequence": record.sequence,
        "timestamp": record.timestamp.isoformat(),
        "rssi": record.rssi,
        "battery_pct": record.battery_pct,
        "metrics": record.metrics,
        "is_simulation": bool(record.is_simulation)
    }


async def get_telemetry_range(
    db: AsyncSession,
    node_id: str,
    minutes: int = 10,
    metric_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve and statistically summarize telemetry over a temporal window (e.g. last 10 minutes).
    Returns compact summary (min, max, average, rate of change, trend).
    """
    since_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    query = (
        select(TelemetryRecord)
        .where(TelemetryRecord.node_id == node_id, TelemetryRecord.timestamp >= since_time)
        .order_by(TelemetryRecord.timestamp.asc())
        .limit(120)
    )
    res = await db.execute(query)
    records = res.scalars().all()

    if not records:
        # Fallback to last 15 records if temporal window is empty in demo
        fallback_query = (
            select(TelemetryRecord)
            .where(TelemetryRecord.node_id == node_id)
            .order_by(desc(TelemetryRecord.timestamp))
            .limit(15)
        )
        fb_res = await db.execute(fallback_query)
        records = fb_res.scalars().all()
        records.reverse()

    as_dicts = [
        {"timestamp": r.timestamp.isoformat(), "metrics": r.metrics}
        for r in records
    ]
    keys = [metric_key] if metric_key else None
    summary = summarize_telemetry_range(node_id, as_dicts, metric_keys=keys)
    summary["window_minutes"] = minutes
    return summary
