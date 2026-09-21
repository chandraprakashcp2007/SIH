"""
Incident Alerts Management API Router
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.alerts import Alert
from backend.app.schemas.models_schema import AlertResponse, AlertAcknowledgeRequest, AlertResolveRequest
from backend.app.services.alert_service import alert_service
from backend.app.api.auth import require_roles

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    state: Optional[str] = Query(None, description="Filter by state: NEW, ACKNOWLEDGED, MONITORING, RESOLVED, ACTIVE"),
    severity: Optional[str] = Query(None, description="Filter by severity: WATCH, WARNING, CRITICAL"),
    node_id: Optional[str] = Query(None, description="Filter by node ID"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """List disaster alerts with filtering and pagination."""
    query = select(Alert)

    if state == "ACTIVE":
        query = query.where(Alert.state.in_(["NEW", "ACKNOWLEDGED", "MONITORING"]))
    elif state:
        query = query.where(Alert.state == state)

    if severity:
        query = query.where(Alert.severity == severity)

    if node_id:
        query = query.where(Alert.node_id == node_id)

    query = query.order_by(desc(Alert.created_at)).limit(limit)
    res = await db.execute(query)
    return res.scalars().all()


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve full details of a specific incident alert."""
    query = select(Alert).where(Alert.id == alert_id)
    res = await db.execute(query)
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: str,
    req: AlertAcknowledgeRequest,
    db: AsyncSession = Depends(get_db),
    _user = Depends(require_roles("ADMIN", "OPERATOR"))
):
    """Operator acknowledgement of an active alert."""
    alert = await alert_service.acknowledge_alert(
        db=db,
        alert_id=alert_id,
        acknowledged_by=req.acknowledged_by or "operator",
        notes=req.notes
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: str,
    req: AlertResolveRequest,
    db: AsyncSession = Depends(get_db),
    _user = Depends(require_roles("ADMIN", "OPERATOR"))
):
    """Resolve an incident with documented operational actions."""
    alert = await alert_service.resolve_alert(
        db=db,
        alert_id=alert_id,
        resolved_by=req.resolved_by or "operator",
        resolution_notes=req.resolution_notes
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
