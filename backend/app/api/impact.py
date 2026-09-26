from fastapi import APIRouter,Depends
from sqlalchemy import desc,func,select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.impact import EvacuationAssessment,ImpactAssessment,InfrastructureAsset,SafeZoneAssessment
from backend.app.websocket.manager import ws_manager

router=APIRouter(tags=["Impact Intelligence"])
def row(x):return {c.name:getattr(x,c.name) for c in x.__table__.columns}

@router.post("/impact/evaluate")
async def impact(db:AsyncSession=Depends(get_db)):
    count=(await db.execute(select(func.count()).select_from(InfrastructureAsset))).scalar_one()
    item=ImpactAssessment(status="NOT_CONFIGURED",population_exposed=None,assets_exposed=None,dependency_impacts=[],provenance="EXTERNAL_DATA",reason="Authoritative population, infrastructure, and dependency datasets are not configured." if not count else "Hazard intersection requires a validated boundary.")
    db.add(item);await db.commit();result=row(item);await ws_manager.broadcast_event("impact.updated",result);return result

@router.get("/impact")
async def impacts(db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(ImpactAssessment).order_by(desc(ImpactAssessment.evaluated_at)).limit(20))).scalars();return [row(x) for x in rows]

@router.post("/evacuation/evaluate")
async def evacuation(db:AsyncSession=Depends(get_db)):
    item=EvacuationAssessment(status="NOT_CONFIGURED",route=None,guaranteed_safe=False,safety_disclaimer="No route can guarantee safety; conditions require continuous field verification.",reliability=None,provenance="EXTERNAL_DATA",reason="Authoritative roads, closures, hazard boundaries, and verified shelters are not configured.")
    db.add(item);await db.commit();result=row(item);await ws_manager.broadcast_event("evacuation.updated",result);return result

@router.get("/safe-zones")
async def zones(db:AsyncSession=Depends(get_db)):
    data=list((await db.execute(select(SafeZoneAssessment).where(SafeZoneAssessment.status=="VERIFIED"))).scalars())
    return {"status":"AVAILABLE" if data else "NOT_CONFIGURED","zones":[row(x) for x in data],"provenance":"EXTERNAL_DATA","reason":None if data else "No authoritative, field-verified safe-zone dataset is configured."}
