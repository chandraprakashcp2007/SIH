from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.cross_hazard import CompoundRiskAssessment, ConsensusAssessment, CrossHazardRelationship
from backend.app.services.cross_hazard_service import cross_hazard_service, _row
from backend.app.websocket.manager import ws_manager

router = APIRouter(tags=["Cross-Hazard Intelligence"])


@router.post("/cascades/reevaluate")
async def reevaluate(db: AsyncSession = Depends(get_db)):
    result = await cross_hazard_service.reevaluate(db)
    active = [item for item in result["relationships"] if item["state"] == "REEVALUATION_REQUIRED"]
    if active:
        await ws_manager.broadcast_event("cascade.detected", {"relationships": active})
    return result


async def _recent(db: AsyncSession, model, limit: int):
    rows = (await db.execute(select(model).order_by(desc(model.evaluated_at)).limit(min(max(limit, 1), 200)))).scalars()
    return [_row(item) for item in rows]


@router.get("/cascades")
async def cascades(limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await _recent(db, CrossHazardRelationship, limit)


@router.get("/compound-risk")
async def compound_risk(limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await _recent(db, CompoundRiskAssessment, limit)


@router.get("/consensus")
async def consensus(limit: int = 50, db: AsyncSession = Depends(get_db)):
    records = await _recent(db, ConsensusAssessment, limit)
    if records:
        return records
    await cross_hazard_service.reevaluate(db)
    return await _recent(db, ConsensusAssessment, limit)
