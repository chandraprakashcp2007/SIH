"""
System & Audit Logs API Router
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.audit import AuditLog

router = APIRouter(prefix="/logs", tags=["System Logs"])


@router.get("")
async def get_logs(
    category: Optional[str] = Query(None, description="Filter: ALERT, SIMULATOR, AUTH, SETTINGS, OPERATIONAL"),
    limit: int = Query(100, ge=10, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve structured audit and operational logs."""
    query = select(AuditLog)
    if category:
        query = query.where(AuditLog.category == category)
    query = query.order_by(desc(AuditLog.timestamp)).limit(limit)

    res = await db.execute(query)
    records = res.scalars().all()

    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat(),
            "action": r.action,
            "category": r.category,
            "component": r.component,
            "user": r.username,
            "message": r.message,
            "details": r.details
        }
        for r in records
    ]
