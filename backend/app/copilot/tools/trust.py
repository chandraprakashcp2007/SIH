"""
Copilot Sensor Trust Tools
Monitors dynamic reliability metrics, anomaly flags, and sensor faults.
"""
from typing import Dict, Any, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.sensor_trust import SensorTrustLog
from backend.app.models.risk import RiskAssessment


async def get_sensor_trust(db: AsyncSession) -> Dict[str, Any]:
    """Retrieve the latest sensor trust scores across all nodes."""
    res = await db.execute(
        select(RiskAssessment)
        .order_by(desc(RiskAssessment.timestamp))
        .limit(6)
    )
    risks = res.scalars().all()
    latest_by_node = {}
    for r in risks:
        if r.node_id not in latest_by_node:
            latest_by_node[r.node_id] = r.sensor_trust

    return {
        "nodes_trust": latest_by_node,
        "trust_threshold_nominal": 80.0
    }


async def get_low_trust_sensors(db: AsyncSession) -> List[Dict[str, Any]]:
    """Identify any transducers currently degraded (< 80%) due to noise, stuck values, or contradictions."""
    res = await db.execute(
        select(SensorTrustLog)
        .where(SensorTrustLog.trust_score < 80.0)
        .order_by(desc(SensorTrustLog.timestamp))
        .limit(20)
    )
    logs = res.scalars().all()
    seen = set()
    low_trust = []
    for l in logs:
        key = (l.node_id, l.sensor_name)
        if key not in seen:
            seen.add(key)
            low_trust.append({
                "node_id": l.node_id,
                "sensor_name": l.sensor_name,
                "trust_score": l.trust_score,
                "anomaly": l.anomaly_detected or "Degraded confidence",
                "timestamp": l.timestamp.isoformat()
            })
    return low_trust
