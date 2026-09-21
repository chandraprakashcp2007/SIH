"""
Telemetry Ingestion & Querying API Router
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.schemas.telemetry import TelemetryIngestPayload, IngestResponse
from backend.app.services.telemetry_service import telemetry_service
from backend.app.models.telemetry import TelemetryRecord

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_telemetry(
    payload: TelemetryIngestPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Primary ingestion endpoint for real LoRa hardware & simulation gateway.
    Receives JSON packet, runs sensor trust, hybrid risk evaluation, persists records,
    creates alerts if necessary, and broadcasts WebSocket event.
    """
    try:
        result = await telemetry_service.ingest_packet(
            db=db,
            payload=payload.model_dump(),
            gateway_source="SIMULATOR" if payload.is_simulation else "USB_SERIAL"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Telemetry processing failed: {str(e)}"
        )


@router.get("/latest")
async def get_latest_telemetry(db: AsyncSession = Depends(get_db)):
    """Retrieve the most recent telemetry packet for each registered node."""
    nodes = ["JALA-01", "AGNI-02", "BHUMI-03"]
    latest = {}
    for nid in nodes:
        query = (
            select(TelemetryRecord)
            .where(TelemetryRecord.node_id == nid)
            .order_by(desc(TelemetryRecord.timestamp))
            .limit(1)
        )
        res = await db.execute(query)
        rec = res.scalar_one_or_none()
        if rec:
            latest[nid] = {
                "sequence": rec.sequence,
                "timestamp": rec.timestamp.isoformat(),
                "rssi": rec.rssi,
                "battery_pct": rec.battery_pct,
                "metrics": rec.metrics
            }
    return latest
