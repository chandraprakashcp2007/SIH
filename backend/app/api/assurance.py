from fastapi import APIRouter,Depends
from sqlalchemy import desc,select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.assurance import AssuranceSnapshot
router=APIRouter(prefix="/assurance",tags=["System Assurance"])
def row(x):return {c.name:getattr(x,c.name) for c in x.__table__.columns}
BLOCKERS=["AUTHORITATIVE_DATASETS_NOT_CONFIGURED","PHYSICAL_HARDWARE_NOT_VERIFIED","PRODUCTION_DEPLOYMENT_NOT_VERIFIED","OFFICIAL_DELIVERY_NOT_CONFIGURED"]
@router.post("/refresh")
async def refresh(db:AsyncSession=Depends(get_db)):
    dimensions={"data_quality":0,"provenance_integrity":0,"security_controls":0,"interoperability_contracts":0,"deployment_evidence":0};item=AssuranceSnapshot(ddqi=0,status="UNVERIFIED",dimensions=dimensions,blockers=BLOCKERS);db.add(item);await db.commit();return row(item)
@router.get("/safety-case")
async def safety_case(db:AsyncSession=Depends(get_db)):
    latest=(await db.execute(select(AssuranceSnapshot).order_by(desc(AssuranceSnapshot.created_at)).limit(1))).scalar_one_or_none()
    if not latest:latest=await refresh(db)
    blockers=latest["blockers"] if isinstance(latest,dict) else latest.blockers
    return {"production_ready":False,"claims":[{"claim":"PROVENANCE_DOMAINS_ARE_SEPARATED","status":"UNVERIFIED","evidence_ids":["CONTRACT:PROVENANCE_ISOLATION"]},{"claim":"SIGNED_TELEMETRY_REJECTIONS_PRECEDE_MUTATION","status":"UNVERIFIED","evidence_ids":["SERVICE:SECURITY_AUDIT_CHAIN"]},{"claim":"INTEROPERABILITY_SUBSETS_ARE_EXPLICIT","status":"UNVERIFIED","evidence_ids":["CONTRACT:SENSORTHINGS_SUBSET","CONTRACT:GEOJSON","CONTRACT:STAC_METADATA"]}],"blockers":blockers}
