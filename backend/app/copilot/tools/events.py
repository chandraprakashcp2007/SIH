"""
Copilot Event & Incident Log Tools
Queries audit records and historical disaster events.
"""
from typing import Dict, Any, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.audit import AuditLog
from backend.app.models.alerts import Alert


async def get_event_details(db: AsyncSession, event_id: str) -> Dict[str, Any]:
    """Retrieve full audit or alert record for a specific event identifier."""
    # First search alerts
    alert_res = await db.execute(select(Alert).where(Alert.id == event_id))
    alert = alert_res.scalar_one_or_none()
    if alert:
        return {
            "type": "ALERT",
            "id": alert.id,
            "node_id": alert.node_id,
            "hazard": alert.hazard,
            "severity": alert.severity,
            "headline": alert.headline,
            "explanation": alert.summary,
            "action": alert.action_recommended,
            "evidence": alert.evidence,
            "timestamp": alert.created_at.isoformat()
        }

    # Then search audit logs
    audit_res = await db.execute(select(AuditLog).where(AuditLog.id == event_id))
    audit = audit_res.scalar_one_or_none()
    if audit:
        return {
            "type": "AUDIT",
            "id": audit.id,
            "action": audit.action,
            "category": audit.category,
            "user": audit.username,
            "message": audit.message,
            "details": audit.details,
            "timestamp": audit.timestamp.isoformat()
        }

    return {"error": f"Event or Incident {event_id} not found."}


async def get_recent_events(db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve the chronological sequence of recent system operational events."""
    res = await db.execute(
        select(AuditLog)
        .order_by(desc(AuditLog.timestamp))
        .limit(limit)
    )
    logs = res.scalars().all()
    return [
        {
            "id": l.id,
            "action": l.action,
            "category": l.category,
            "message": l.message,
            "timestamp": l.timestamp.isoformat()
        }
        for l in logs
    ]
