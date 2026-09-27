import hashlib,json
from datetime import datetime,timezone
from fastapi import APIRouter,Body,Depends,HTTPException
from sqlalchemy import desc,select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.disaster_memory import DisasterMemory

router=APIRouter(prefix="/memory",tags=["Disaster Memory"]);ZERO="0"*64
def row(x):return {c.name:getattr(x,c.name) for c in x.__table__.columns}
def fingerprint(hazard,features):return hashlib.sha256(json.dumps({"hazard":hazard,"features":features},sort_keys=True,separators=(",",":")).encode()).hexdigest()
def entry_hash(item):
    material={"hazard":item.hazard,"fingerprint":item.fingerprint,"features":item.features,"evidence_ids":item.evidence_ids,"provenance":item.provenance,"previous_hash":item.previous_hash,"created_at":item.created_at.replace(tzinfo=timezone.utc).isoformat()}
    return hashlib.sha256(json.dumps(material,sort_keys=True,separators=(",",":")).encode()).hexdigest()

@router.get("/events")
async def events(db:AsyncSession=Depends(get_db)):return [row(x) for x in (await db.execute(select(DisasterMemory).order_by(desc(DisasterMemory.created_at)))).scalars()]
@router.post("/events")
async def create(payload:dict=Body(...),db:AsyncSession=Depends(get_db)):
    previous=(await db.execute(select(DisasterMemory).order_by(desc(DisasterMemory.created_at),desc(DisasterMemory.id)).limit(1))).scalar_one_or_none();created=datetime.now(timezone.utc)
    item=DisasterMemory(hazard=payload.get("hazard","UNKNOWN"),fingerprint=fingerprint(payload.get("hazard","UNKNOWN"),payload.get("features",{})),features=payload.get("features",{}),evidence_ids=payload.get("evidence_ids",[]),provenance=payload.get("provenance","SIMULATION"),previous_hash=previous.entry_hash if previous else ZERO,entry_hash="pending",created_at=created);item.entry_hash=entry_hash(item);db.add(item);await db.commit();return row(item)
@router.get("/events/{event_id}/similar")
async def similar(event_id:str,db:AsyncSession=Depends(get_db)):
    target=await db.get(DisasterMemory,event_id)
    if not target:raise HTTPException(404,"MEMORY_NOT_FOUND")
    matches=(await db.execute(select(DisasterMemory).where(DisasterMemory.id!=event_id,DisasterMemory.hazard==target.hazard))).scalars()
    return [{"event_id":x.id,"score":1.0 if x.fingerprint==target.fingerprint else 0.0,"evidence_ids":x.evidence_ids} for x in matches if x.fingerprint==target.fingerprint]
@router.post("/events/{event_id}/replay")
async def replay(event_id:str,db:AsyncSession=Depends(get_db)):
    item=await db.get(DisasterMemory,event_id)
    if not item:raise HTTPException(404,"MEMORY_NOT_FOUND")
    return {"event_id":item.id,"source_mode":"REPLAY","operational_mutation":False,"features":item.features,"evidence_ids":item.evidence_ids}
@router.get("/black-box/verify")
async def verify(db:AsyncSession=Depends(get_db)):
    items=list((await db.execute(select(DisasterMemory).order_by(DisasterMemory.created_at,DisasterMemory.id))).scalars());previous=ZERO
    for item in items:
        if item.previous_hash!=previous or item.entry_hash!=entry_hash(item):return {"valid":False,"entries":len(items),"failed_id":item.id}
        previous=item.entry_hash
    return {"valid":True,"entries":len(items),"head":previous}
