import hashlib,hmac,json,os
from datetime import datetime,timezone
from fastapi import APIRouter,Body,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.security import SecurityEvent,TelemetryNonce
from backend.app.services.security_service import ZERO,append_security_event,expected_hash
from backend.app.services.telemetry_service import telemetry_service
from backend.app.websocket.manager import ws_manager
router=APIRouter(prefix="/security",tags=["Security"])
def row(x):return {c.name:getattr(x,c.name) for c in x.__table__.columns}
def keys():
    try:return json.loads(os.getenv("PRAHARI_DEVICE_KEYS","{}"))
    except json.JSONDecodeError:return {}
@router.get("/status")
async def status():return {"signed_telemetry":"CONFIGURED" if keys() else "NOT_CONFIGURED","key_storage":"SERVER_ENVIRONMENT","replay_protection":"ACTIVE","audit_chain":"ACTIVE"}
@router.post("/telemetry/ingest")
async def ingest(envelope:dict=Body(...),db:AsyncSession=Depends(get_db)):
    node=envelope.get("node_id");nonce=envelope.get("nonce");signature=envelope.get("signature","");secret=keys().get(node)
    if not secret:raise HTTPException(503,"DEVICE_KEY_NOT_CONFIGURED")
    unsigned={k:v for k,v in envelope.items() if k!="signature"};canonical=json.dumps(unsigned,sort_keys=True,separators=(",",":"));expected=hmac.new(secret.encode(),canonical.encode(),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,signature):
        await append_security_event(db,"INVALID_SIGNATURE","HIGH",node,{"nonce":nonce});await db.commit();raise HTTPException(401,"INVALID_SIGNATURE")
    seen=(await db.execute(select(TelemetryNonce).where(TelemetryNonce.node_id==node,TelemetryNonce.nonce==nonce))).scalar_one_or_none()
    if seen:
        event=await append_security_event(db,"REPLAY_DETECTED","HIGH",node,{"nonce":nonce});await db.commit();await ws_manager.broadcast_event("security.event",row(event));raise HTTPException(409,"REPLAY_DETECTED")
    try:sent=datetime.fromisoformat(envelope["timestamp"].replace("Z","+00:00"));sent=sent if sent.tzinfo else sent.replace(tzinfo=timezone.utc)
    except Exception:raise HTTPException(422,"INVALID_TIMESTAMP")
    if abs((datetime.now(timezone.utc)-sent.astimezone(timezone.utc)).total_seconds())>300:raise HTTPException(422,"STALE_SIGNED_ENVELOPE")
    db.add(TelemetryNonce(node_id=node,nonce=nonce,signature_fingerprint=hashlib.sha256(signature.encode()).hexdigest()))
    event=await append_security_event(db,"SIGNED_TELEMETRY_ACCEPTED","INFO",node,{"nonce":nonce});await db.flush()
    payload=dict(envelope.get("payload") or {});payload.update({"node_id":node,"timestamp":envelope["timestamp"],"source_mode":"REAL","is_simulation":False,"transport":"SIGNED_GATEWAY"})
    result=await telemetry_service.ingest_packet(db,payload,"SIGNED_GATEWAY");await db.commit();await ws_manager.broadcast_event("security.event",row(event));return {"security_state":"VERIFIED","telemetry":result}
@router.get("/events")
async def events(db:AsyncSession=Depends(get_db)):
    rows=list((await db.execute(select(SecurityEvent).order_by(SecurityEvent.created_at.desc()).limit(100))).scalars());return [row(x) for x in rows]
@router.get("/audit-chain/verify")
async def verify(db:AsyncSession=Depends(get_db)):
    rows=list((await db.execute(select(SecurityEvent).order_by(SecurityEvent.created_at,SecurityEvent.id))).scalars());previous=ZERO
    for item in rows:
        if item.previous_hash!=previous or item.event_hash!=expected_hash(item):return {"valid":False,"entries":len(rows),"failed_id":item.id}
        previous=item.event_hash
    return {"valid":True,"entries":len(rows),"head":previous}
