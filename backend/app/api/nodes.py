"""
System Status & Node Management API Endpoints
"""
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.nodes import Node
from backend.app.models.telemetry import TelemetryRecord
from backend.app.models.risk import RiskAssessment
from backend.app.models.alerts import Alert
from backend.app.core.config import settings
from gateway.simulator import prahari_sim
from backend.app.services.readiness_service import get_gateway_state
from backend.app.services.simulation_service import simulation_service

router = APIRouter(prefix="", tags=["System & Nodes"])


@router.get("/system/summary")
async def system_summary(db: AsyncSession = Depends(get_db)):
    """Operational status summary for the command-centre topbar and widgets."""
    nodes_res = await db.execute(select(Node))
    nodes = nodes_res.scalars().all()

    alerts_res = await db.execute(
        select(Alert).where(Alert.state.in_(["NEW", "ACKNOWLEDGED", "MONITORING"]))
    )
    active_alerts = alerts_res.scalars().all()

    # Determine network mode
    # If internet outage scenario is simulated, show LOCAL_EDGE
    network_mode = "LOCAL_EDGE" if prahari_sim.internet_outage else "ONLINE"

    # Average risk score across active nodes
    risks_res = await db.execute(
        select(RiskAssessment)
        .order_by(desc(RiskAssessment.timestamp))
        .limit(3)
    )
    latest_risks = risks_res.scalars().all()
    avg_risk = round(sum(r.risk_score for r in latest_risks) / max(1, len(latest_risks)), 1)

    gateway = await get_gateway_state(db)
    return {
        "nodes_total": len(nodes),
        "nodes_online": len([n for n in nodes if n.status != "OFFLINE"]),
        "active_alerts_count": len(active_alerts),
        "critical_alerts_count": len([a for a in active_alerts if a.severity == "CRITICAL"]),
        "warning_alerts_count": len([a for a in active_alerts if a.severity == "WARNING"]),
        "network_mode": network_mode,
        "gateway_status": gateway["status"],
        "last_packet_age_seconds": gateway["last_packet_age_seconds"],
        "gateway_mode": settings.GATEWAY_MODE,
        "simulation_active": simulation_service.is_running,
        "average_risk": avg_risk,
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/system/health")
async def system_health():
    """Liveness health-check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.VERSION,
        "database": "sqlite_wal_active",
        "gateway": settings.GATEWAY_MODE
    }


@router.get("/nodes")
async def list_nodes(db: AsyncSession = Depends(get_db)):
    """List all registered nodes with their latest risk and metric summaries."""
    res = await db.execute(select(Node))
    nodes = res.scalars().all()
    results = []

    for n in nodes:
        # Fetch latest risk
        risk_res = await db.execute(
            select(RiskAssessment)
            .where(RiskAssessment.node_id == n.id)
            .order_by(desc(RiskAssessment.timestamp))
            .limit(1)
        )
        latest_risk = risk_res.scalar_one_or_none()

        # Fetch latest telemetry
        telem_res = await db.execute(
            select(TelemetryRecord)
            .where(TelemetryRecord.node_id == n.id)
            .order_by(desc(TelemetryRecord.timestamp))
            .limit(1)
        )
        latest_telem = telem_res.scalar_one_or_none()

        results.append({
            "id": n.id,
            "name": n.name,
            "node_type": n.node_type,
            "tagline": n.tagline,
            "latitude": n.latitude,
            "longitude": n.longitude,
            "elevation_m": n.elevation_m,
            "location_name": n.location_name,
            "status": n.status,
            "firmware_version": n.firmware_version,
            "hardware_rev": n.hardware_rev,
            "battery_pct": n.battery_pct,
            "solar_voltage": n.solar_voltage,
            "signal_rssi": n.signal_rssi,
            "packet_loss_pct": n.packet_loss_pct,
            "last_seen": n.last_seen.isoformat(),
            "sensors_configured": n.sensors_configured,
            "source_mode": n.source_mode,
            "hardware_profile": n.hardware_profile or {},
            "latest_risk": {
                "risk_score": latest_risk.risk_score if latest_risk else 0.0,
                "risk_band": latest_risk.risk_band if latest_risk else "NORMAL",
                "confidence": latest_risk.confidence if latest_risk else 100.0,
                "anomaly_score": latest_risk.anomaly_score if latest_risk else 0.0,
                "sensor_trust": latest_risk.sensor_trust if latest_risk else {},
                "contributing_factors": latest_risk.contributing_factors if latest_risk else [],
                "human_explanation": latest_risk.human_explanation if latest_risk else "Nominal status",
                "recommended_action": latest_risk.recommended_action if latest_risk else "Routine surveillance",
                "estimated_crossing_time": latest_risk.estimated_crossing_time if latest_risk else None,
                "risk_trend": latest_risk.risk_trend if latest_risk else "STABLE"
            } if latest_risk else None,
            "latest_metrics": latest_telem.metrics if latest_telem else {}
            ,"latest_source_mode": latest_telem.source_mode if latest_telem else n.source_mode
        })

    return results


@router.get("/nodes/{node_id}")
async def get_node(node_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve detailed metadata and current telemetry for a single node."""
    res = await db.execute(select(Node).where(Node.id == node_id))
    node = res.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    risk_res = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.node_id == node_id)
        .order_by(desc(RiskAssessment.timestamp))
        .limit(1)
    )
    latest_risk = risk_res.scalar_one_or_none()

    telem_res = await db.execute(
        select(TelemetryRecord)
        .where(TelemetryRecord.node_id == node_id)
        .order_by(desc(TelemetryRecord.timestamp))
        .limit(1)
    )
    latest_telem = telem_res.scalar_one_or_none()

    return {
        "id": node.id,
        "name": node.name,
        "node_type": node.node_type,
        "tagline": node.tagline,
        "latitude": node.latitude,
        "longitude": node.longitude,
        "elevation_m": node.elevation_m,
        "location_name": node.location_name,
        "status": node.status,
        "firmware_version": node.firmware_version,
        "hardware_rev": node.hardware_rev,
        "battery_pct": node.battery_pct,
        "solar_voltage": node.solar_voltage,
        "signal_rssi": node.signal_rssi,
        "packet_loss_pct": node.packet_loss_pct,
        "last_seen": node.last_seen.isoformat(),
        "sensors_configured": node.sensors_configured,
        "source_mode": node.source_mode,
        "hardware_profile": node.hardware_profile or {},
        "latest_risk": latest_risk,
        "latest_metrics": latest_telem.metrics if latest_telem else {},
        "latest_source_mode": latest_telem.source_mode if latest_telem else node.source_mode
    }


@router.get("/nodes/{node_id}/telemetry")
async def get_node_telemetry(
    node_id: str,
    limit: int = 60,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve historical time-series telemetry points for graphing."""
    query = (
        select(TelemetryRecord)
        .where(TelemetryRecord.node_id == node_id)
        .order_by(desc(TelemetryRecord.timestamp))
        .limit(limit)
    )
    res = await db.execute(query)
    records = res.scalars().all()
    records.reverse()  # Chronological order
    return [
        {
            "id": r.id,
            "sequence": r.sequence,
            "timestamp": r.timestamp.isoformat(),
            "rssi": r.rssi,
            "battery_pct": r.battery_pct,
            "metrics": r.metrics
        }
        for r in records
    ]


@router.get("/nodes/{node_id}/risk")
async def get_node_risk_history(
    node_id: str,
    limit: int = 60,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve historical risk assessments for a node."""
    query = (
        select(RiskAssessment)
        .where(RiskAssessment.node_id == node_id)
        .order_by(desc(RiskAssessment.timestamp))
        .limit(limit)
    )
    res = await db.execute(query)
    records = res.scalars().all()
    records.reverse()
    return records
