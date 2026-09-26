import hashlib,json
from datetime import datetime,timezone
from fastapi import APIRouter,Body,Depends,HTTPException
from sqlalchemy import desc,select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.continuity import ContinuitySnapshot,OutboundQueueItem
from backend.app.websocket.manager import ws_manager
router=APIRouter(prefix="/continuity",tags=["Continuity"])
def row(x):return {c.name:getattr(x,c.name) for c in x.__table__.columns}
@router.post("/queue")
async def queue(payload:dict=Body(...),db:AsyncSession=Depends(get_db)):
    canonical=json.dumps({"operation":payload.get("operation"),"body":payload.get("body"),"provenance":payload.get("provenance")},sort_keys=True,separators=(",",":"));checksum=hashlib.sha256(canonical.encode()).hexdigest()
    existing=(await db.execute(select(OutboundQueueItem).where(OutboundQueueItem.checksum==checksum))).scalar_one_or_none()
    if existing:return row(existing)
    provenance=payload.get("provenance");
    if provenance not in {"REAL","EXTERNAL_DATA","MODEL","SIMULATION","REPLAY","PLANNED"}:raise HTTPException(422,"Invalid provenance")
    item=OutboundQueueItem(checksum=checksum,operation=payload.get("operation","UNKNOWN"),body=payload.get("body") or {},provenance=provenance);db.add(item);await db.commit();return row(item)
@router.post("/queue/{item_id}/ack")
async def ack(item_id:str,db:AsyncSession=Depends(get_db)):
    item=(await db.execute(select(OutboundQueueItem).where(OutboundQueueItem.id==item_id))).scalar_one_or_none()
    if not item:raise HTTPException(404,"Queue item not found")
    if item.state!="ACKNOWLEDGED":item.state="ACKNOWLEDGED";item.acknowledged_at=datetime.now(timezone.utc);await db.commit();await ws_manager.broadcast_event("continuity.queue.acknowledged",{"id":item.id,"checksum":item.checksum})
    return row(item)
@router.get("/queue")
async def queued(db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(OutboundQueueItem).order_by(desc(OutboundQueueItem.created_at)).limit(100))).scalars();return [row(x) for x in rows]
@router.post("/evaluate")
async def evaluate(payload:dict=Body(...),db:AsyncSession=Depends(get_db)):
    internet=bool(payload.get("internet"));gateway=bool(payload.get("gateway"));wifi=bool(payload.get("local_wifi"));external=bool(payload.get("external_data"))
    if not external and (internet or wifi):mode="EXTERNAL_DATA_DEGRADED"
    elif internet and gateway:mode="FULL_ONLINE"
    elif wifi:mode="LOCAL_WIFI"
    elif gateway:mode="LOCAL_EDGE"
    else:mode="STORE_FORWARD"
    battery=float(payload.get("battery_pct",100));energy="CONSERVE" if battery<25 else "BALANCED" if battery<60 else "FULL";network="LOW_BANDWIDTH" if not internet else "NORMAL"
    item=ContinuitySnapshot(mode=mode,link_state=payload,energy_policy=energy,network_policy=network,reason="Mode derived from reported link availability; cached data remains stale until synchronized.");db.add(item);await db.commit();result=row(item);await ws_manager.broadcast_event("continuity.mode.changed",result);return result
@router.get("/status")
async def status(db:AsyncSession=Depends(get_db)):
    item=(await db.execute(select(ContinuitySnapshot).order_by(desc(ContinuitySnapshot.evaluated_at)).limit(1))).scalar_one_or_none();return row(item) if item else {"mode":"NOT_EVALUATED","energy_policy":"UNKNOWN","network_policy":"UNKNOWN","link_state":{},"reason":"No continuity evaluation has been recorded."}
@router.get("/transports")
async def transports():return [{"transport":"WIFI","state":"SUPPORTED"},{"transport":"USB_SERIAL","state":"SUPPORTED"},{"transport":"LORA","state":"PLANNED"},{"transport":"LORAWAN","state":"PLANNED"},{"transport":"NB_IOT","state":"UNAVAILABLE"},{"transport":"CELLULAR","state":"NOT_CONFIGURED"},{"transport":"5G","state":"PLANNED"}]
