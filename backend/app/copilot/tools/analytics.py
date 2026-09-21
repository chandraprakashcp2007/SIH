"""
Copilot Analytics Tools
Summarizes incident trends, hazard distributions, and average acknowledgement latency.
"""
from typing import Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.alerts import Alert
from backend.app.models.network import GatewayPacketLog


async def get_analytics_summary(db: AsyncSession) -> Dict[str, Any]:
    """Retrieve macro-level statistics on hazard incidents and operator response times."""
    res = await db.execute(select(Alert))
    alerts = res.scalars().all()

    by_hazard = {"FLOOD": 0, "FIRE": 0, "LANDSLIDE": 0}
    by_severity = {"WATCH": 0, "WARNING": 0, "CRITICAL": 0}
    total_ack_sec = 0.0
    acked_count = 0

    for a in alerts:
        if a.hazard in by_hazard:
            by_hazard[a.hazard] += 1
        if a.severity in by_severity:
            by_severity[a.severity] += 1
        if a.acknowledged_at and a.created_at:
            delta = (a.acknowledged_at - a.created_at).total_seconds()
            if delta >= 0:
                total_ack_sec += delta
                acked_count += 1

    avg_ack = round(total_ack_sec / max(1, acked_count), 1)

    return {
        "total_alerts": len(alerts),
        "alerts_by_hazard": by_hazard,
        "alerts_by_severity": by_severity,
        "average_ack_time_seconds": avg_ack,
        "active_incidents": len([a for a in alerts if a.state in ("NEW", "ACKNOWLEDGED", "MONITORING")])
    }
