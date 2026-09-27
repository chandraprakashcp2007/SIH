from fastapi import APIRouter,Body,Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.recovery import DamageEvidence,RecoveryReport
from backend.app.api.auth import require_roles
from backend.app.models.users import User
from datetime import datetime,timezone
router=APIRouter(prefix="/recovery",tags=["Recovery Intelligence"])
def row(x):return {c.name:getattr(x,c.name) for c in x.__table__.columns}
@router.get("/evidence")
async def evidence(incident_id:str|None=None,db:AsyncSession=Depends(get_db)):
    q=select(DamageEvidence);q=q.where(DamageEvidence.incident_id==incident_id) if incident_id else q;return [row(x) for x in (await db.execute(q)).scalars()]
@router.post("/evidence")
async def add_evidence(payload:dict=Body(...),db:AsyncSession=Depends(get_db),user:User=Depends(require_roles("ADMIN","OPERATOR"))):
    verified=payload.get("human_verified") is True and bool(payload.get("artifact_reference"));now=datetime.now(timezone.utc) if verified else None;item=DamageEvidence(incident_id=payload.get("incident_id","UNASSIGNED"),kind=payload.get("kind","OBSERVATION"),provenance=payload.get("provenance","EXTERNAL_DATA"),description=payload.get("description",""),artifact_reference=payload.get("artifact_reference"),human_verified=verified,verified_by=user.username if verified else None,verified_at=now,verification_state="HUMAN_VERIFIED" if verified else "PENDING_HUMAN_VERIFICATION");db.add(item);await db.commit();return row(item)
@router.post("/reports")
async def report(payload:dict=Body(...),db:AsyncSession=Depends(get_db),user:User=Depends(require_roles("ADMIN","OPERATOR"))):
    incident=payload.get("incident_id","UNASSIGNED");items=list((await db.execute(select(DamageEvidence).where(DamageEvidence.incident_id==incident))).scalars());all_verified=bool(items) and all(x.human_verified and x.provenance not in {"SIMULATION","REPLAY","PLANNED"} for x in items);status="VERIFIED_RECOVERY_REVIEW" if all_verified else "ASSESSMENT_PENDING";provenance="EXTERNAL_DATA" if all_verified else "PLANNED";report=RecoveryReport(incident_id=incident,evidence_ids=[x.id for x in items],provenance=provenance,recovery_status=status,auto_all_clear=False,narrative=f"Recovery status {status}; based on {len(items)} persisted evidence item(s). Human authority must issue any all-clear.");db.add(report);await db.commit();return row(report)
