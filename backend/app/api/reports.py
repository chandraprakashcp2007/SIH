"""
Reports & CSV Data Export API Router
"""
import io
import csv
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.telemetry import TelemetryRecord
from backend.app.models.alerts import Alert
from backend.app.models.audit import AuditLog

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/export/csv")
async def export_csv(
    report_type: str = Query("telemetry", description="Type: telemetry, alerts, events"),
    node_id: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=5000),
    db: AsyncSession = Depends(get_db)
):
    """Export tabular disaster data as downloadable CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == "telemetry":
        writer.writerow(["Device Timestamp", "Server Received", "Node ID", "Sequence", "RSSI (dBm)", "Battery (%)", "Source Mode", "Metrics"])
        query = select(TelemetryRecord)
        if node_id:
            query = query.where(TelemetryRecord.node_id == node_id)
        query = query.order_by(desc(TelemetryRecord.timestamp)).limit(limit)
        res = await db.execute(query)
        records = res.scalars().all()
        for r in records:
            writer.writerow([r.device_timestamp.isoformat(), r.server_received_at.isoformat(), r.node_id, r.sequence, r.rssi, r.battery_pct, r.source_mode, str(r.metrics)])
        filename = f"prahari_telemetry_{node_id or 'all'}.csv"

    elif report_type == "alerts":
        writer.writerow(["Alert ID", "Severity", "Hazard", "Node ID", "Created At", "State", "Confidence", "Risk Score", "Headline", "Acknowledged By", "Resolved By"])
        query = select(Alert).order_by(desc(Alert.created_at)).limit(limit)
        res = await db.execute(query)
        records = res.scalars().all()
        for a in records:
            writer.writerow([a.id, a.severity, a.hazard, a.node_id, a.created_at.isoformat(), a.state, a.confidence, a.risk_score, a.headline, a.acknowledged_by or "", a.resolved_by or ""])
        filename = "prahari_incident_alerts.csv"

    elif report_type == "events":
        writer.writerow(["Timestamp", "Action", "Category", "Component", "User", "Message"])
        query = select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit)
        res = await db.execute(query)
        records = res.scalars().all()
        for e in records:
            writer.writerow([e.timestamp.isoformat(), e.action, e.category, e.component, e.username, e.message])
        filename = "prahari_audit_event_history.csv"

    else:
        raise HTTPException(status_code=400, detail="Invalid report_type. Use: telemetry, alerts, events")

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/incident/{alert_id}")
async def get_incident_report(alert_id: str, db: AsyncSession = Depends(get_db)):
    """Formatted printable incident report for emergency response authorities."""
    query = select(Alert).where(Alert.id == alert_id)
    res = await db.execute(query)
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert incident not found")

    return {
        "organization": "PRAHARI-NET Emergency Command Centre",
        "competition": "Smart India Hackathon 2026 - SIH26178",
        "incident_id": alert.id,
        "hazard_category": alert.hazard,
        "reporting_node": alert.node_id,
        "location": alert.location_name,
        "severity_level": alert.severity,
        "detection_timestamp": alert.created_at.isoformat(),
        "risk_assessment_score": alert.risk_score,
        "detection_confidence_pct": alert.confidence,
        "executive_summary": alert.summary,
        "operational_action_taken": alert.action_recommended,
        "lifecycle_state": alert.state,
        "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        "acknowledged_by": alert.acknowledged_by,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        "resolved_by": alert.resolved_by,
        "resolution_notes": alert.resolution_notes or "Active investigation underway.",
        "telemetry_evidence": alert.evidence
    }
