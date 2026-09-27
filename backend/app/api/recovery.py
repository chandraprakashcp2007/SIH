from fastapi import APIRouter,Body,Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.recovery import DamageEvidence,RecoveryReport
router=APIRouter(prefix="/recovery",tags=["Recovery Intelligence"])
def row(x):return {c.name:getattr(x,c.name) for c in x.__table__.columns}
@router.get("/evidence")
async def evidence(incident_id:str|None=None,db:AsyncSession=Depends(get_db)):
    q=select(DamageEvidence);q=q.where(DamageEvidence.incident_id==incident_id) if incident_id else q;return [row(x) for x in (await db.execute(q)).scalars()]
@router.post("/evidence")
async def add_evidence(payload:dict=Body(...),db:AsyncSession=Depends(get_db)):
    verified=payload.get("human_verified") is True;item=DamageEvidence(incident_id=payload.get("incident_id","UNASSIGNED"),kind=payload.get("kind","OBSERVATION"),provenance=payload.get("provenance","EXTERNAL_DATA"),description=payload.get("description",""),human_verified=verified,verification_state="HUMAN_VERIFIED" if verified else "PENDING_HUMAN_VERIFICATION");db.add(item);await db.commit();return row(item)
@router.post("/reports")
async def report(payload:dict=Body(...),db:AsyncSession=Depends(get_db)):
    incident=payload.get("incident_id","UNASSIGNED");items=list((await db.execute(select(DamageEvidence).where(DamageEvidence.incident_id==incident))).scalars());all_verified=bool(items) and all(x.human_verified for x in items);status="VERIFIED_RECOVERY_REVIEW" if all_verified else "ASSESSMENT_PENDING";report=RecoveryReport(incident_id=incident,evidence_ids=[x.id for x in items],recovery_status=status,auto_all_clear=False,narrative=f"Recovery status {status}; based on {len(items)} persisted evidence item(s). Human authority must issue any all-clear.");db.add(report);await db.commit();return row(report)
