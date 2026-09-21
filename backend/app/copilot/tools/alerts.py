"""
Copilot Alerts & Risk Assessment Tools
Queries active and unacknowledged disaster incidents and causal evidence.
"""
from typing import Dict, Any, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.alerts import Alert
from backend.app.models.risk import RiskAssessment


async def get_active_alerts(db: AsyncSession) -> List[Dict[str, Any]]:
    """Retrieve all currently active (NEW, ACKNOWLEDGED, MONITORING) emergency alerts."""
    res = await db.execute(
        select(Alert)
        .where(Alert.state.in_(["NEW", "ACKNOWLEDGED", "MONITORING"]))
        .order_by(desc(Alert.created_at))
        .limit(20)
    )
    alerts = res.scalars().all()
    return [
        {
            "id": a.id,
            "severity": a.severity,
            "hazard": a.hazard,
            "node_id": a.node_id,
            "location_name": a.location_name,
            "state": a.state,
            "headline": a.headline,
            "risk_score": a.risk_score,
            "created_at": a.created_at.isoformat(),
            "action_recommended": a.action_recommended
        }
        for a in alerts
    ]


async def get_unacknowledged_alerts(db: AsyncSession) -> List[Dict[str, Any]]:
    """Retrieve all NEW unacknowledged disaster alerts requiring operator attention."""
    res = await db.execute(
        select(Alert)
        .where(Alert.state == "NEW")
        .order_by(desc(Alert.created_at))
        .limit(20)
    )
    alerts = res.scalars().all()
    return [
        {
            "id": a.id,
            "severity": a.severity,
            "hazard": a.hazard,
            "node_id": a.node_id,
            "headline": a.headline,
            "created_at": a.created_at.isoformat(),
            "action_recommended": a.action_recommended
        }
        for a in alerts
    ]


async def get_alert_details(db: AsyncSession, alert_id: str) -> Dict[str, Any]:
    """Retrieve full causal evidence and metrics for a specific incident."""
    res = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = res.scalar_one_or_none()
    if not alert:
        return {"error": f"Alert {alert_id} not found."}

    return {
        "id": alert.id,
        "severity": alert.severity,
        "hazard": alert.hazard,
        "node_id": alert.node_id,
        "location_name": alert.location_name,
        "state": alert.state,
        "headline": alert.headline,
        "summary": alert.summary,
        "action_recommended": alert.action_recommended,
        "confidence": alert.confidence,
        "risk_score": alert.risk_score,
        "evidence": alert.evidence,
        "created_at": alert.created_at.isoformat(),
        "acknowledged_by": alert.acknowledged_by,
        "resolution_notes": alert.resolution_notes
    }


async def get_risk_assessment(db: AsyncSession, node_id: str) -> Dict[str, Any]:
    """Retrieve the authoritative calculated risk score and factor weights for a node."""
    res = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.node_id == node_id)
        .order_by(desc(RiskAssessment.timestamp))
        .limit(1)
    )
    risk = res.scalar_one_or_none()
    if not risk:
        return {"error": f"No risk assessment found for {node_id}."}

    return {
        "node_id": risk.node_id,
        "risk_score": risk.risk_score,
        "risk_band": risk.risk_band,
        "confidence": risk.confidence,
        "anomaly_score": risk.anomaly_score,
        "sensor_trust": risk.sensor_trust,
        "contributing_factors": risk.contributing_factors,
        "human_explanation": risk.human_explanation,
        "recommended_action": risk.recommended_action,
        "model_source": risk.model_source,
        "estimated_crossing_time": risk.estimated_crossing_time,
        "risk_trend": risk.risk_trend,
        "timestamp": risk.timestamp.isoformat()
    }
