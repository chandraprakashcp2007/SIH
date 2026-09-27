import hashlib,json
from fastapi import APIRouter,Body,Depends
from sqlalchemy import desc,select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.laboratory import LaboratoryRun
router=APIRouter(prefix="/lab",tags=["Scenario and Chaos Laboratory"])
def row(x):return {c.name:getattr(x,c.name) for c in x.__table__.columns}
async def persist(db,kind,name,seed,inputs):
    material={"kind":kind,"name":name,"seed":seed,"inputs":inputs};digest=hashlib.sha256(json.dumps(material,sort_keys=True,separators=(",",":")).encode()).hexdigest();item=LaboratoryRun(kind=kind,name=name,seed=seed,inputs=inputs,result_digest=digest,provenance="SIMULATION");db.add(item);await db.commit();return item
@router.get("/runs")
async def runs(db:AsyncSession=Depends(get_db)):return [row(x) for x in (await db.execute(select(LaboratoryRun).order_by(desc(LaboratoryRun.created_at)))).scalars()]
@router.post("/scenarios/run")
async def scenario(payload:dict=Body(...),db:AsyncSession=Depends(get_db)):
    item=await persist(db,"SCENARIO",payload.get("scenario","UNNAMED"),int(payload.get("seed",0)),payload.get("parameters",{}));return {**row(item),"operational_mutation":False}
@router.post("/chaos/run")
async def chaos(payload:dict=Body(...),db:AsyncSession=Depends(get_db)):
    faults=list(payload.get("faults",[]));item=await persist(db,"CHAOS","FAULT_INJECTION",int(payload.get("seed",0)),{"faults":faults});return {**row(item),"faults":faults,"operational_mutation":False,"real_state_strengthened":False}
