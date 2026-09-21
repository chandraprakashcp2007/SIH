"""
Copilot Node Tools
Queries fleet node states, locations, RF telemetry, and latest risk assessments.
"""
from typing import Dict, Any, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.nodes import Node
from backend.app.models.risk import RiskAssessment
from backend.app.models.telemetry import TelemetryRecord


async def get_node_status(db: AsyncSession, node_id: str) -> Dict[str, Any]:
    """Retrieve in-depth telemetry and risk status for a designated node."""
    res = await db.execute(select(Node).where(Node.id == node_id))
    node = res.scalar_one_or_none()
    if not node:
        return {"error": f"Node {node_id} not found in database."}

    # Fetch latest risk assessment
    risk_res = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.node_id == node_id)
        .order_by(desc(RiskAssessment.timestamp))
        .limit(1)
    )
    latest_risk = risk_res.scalar_one_or_none()

    # Fetch latest telemetry record
    telem_res = await db.execute(
        select(TelemetryRecord)
        .where(TelemetryRecord.node_id == node_id)
        .order_by(desc(TelemetryRecord.timestamp))
        .limit(1)
    )
    latest_telem = telem_res.scalar_one_or_none()

    return {
        "node_id": node.id,
        "name": node.name,
        "node_type": node.node_type,
        "location_name": node.location_name,
        "status": node.status,
        "battery_pct": node.battery_pct,
        "signal_rssi": node.signal_rssi,
        "packet_loss_pct": node.packet_loss_pct,
        "last_seen": node.last_seen.isoformat() if node.last_seen else None,
        "current_risk_score": latest_risk.risk_score if latest_risk else 0.0,
        "current_risk_band": latest_risk.risk_band if latest_risk else "NORMAL",
        "confidence": latest_risk.confidence if latest_risk else 100.0,
        "explanation": latest_risk.human_explanation if latest_risk else "Nominal baseline readings.",
        "recommended_action": latest_risk.recommended_action if latest_risk else "Routine observation.",
        "latest_metrics": latest_telem.metrics if latest_telem else {}
    }


async def get_all_nodes(db: AsyncSession) -> List[Dict[str, Any]]:
    """List summary status for all registered sensor nodes."""
    res = await db.execute(select(Node))
    nodes = res.scalars().all()
    results = []

    for n in nodes:
        risk_res = await db.execute(
            select(RiskAssessment)
            .where(RiskAssessment.node_id == n.id)
            .order_by(desc(RiskAssessment.timestamp))
            .limit(1)
        )
        r = risk_res.scalar_one_or_none()
        results.append({
            "node_id": n.id,
            "name": n.name,
            "node_type": n.node_type,
            "status": n.status,
            "rssi": n.signal_rssi,
            "battery_pct": n.battery_pct,
            "packet_loss_pct": n.packet_loss_pct,
            "risk_score": r.risk_score if r else 0.0,
            "risk_band": r.risk_band if r else "NORMAL"
        })
    return results
