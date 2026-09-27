import hashlib,hmac,json,os
from datetime import datetime,timezone
from fastapi import APIRouter,Body,Depends,HTTPException
from pydantic import ValidationError
from sqlalchemy import select,update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.security import SecurityEvent,SecureDeviceState,TelemetryNonce
from backend.app.schemas.telemetry import TelemetryIngestPayload
from backend.app.services.security_service import ZERO,append_security_event,expected_hash
from backend.app.services.telemetry_service import telemetry_service
from backend.app.websocket.manager import ws_manager
router=APIRouter(prefix="/security",tags=["Security"])
def row(x):return {c.name:getattr(x,c.name) for c in x.__table__.columns}
def keys():
    try:return json.loads(os.getenv("PRAHARI_DEVICE_KEYS","{}"))
    except json.JSONDecodeError:return {}
async def reject(db,event_type,status_code,node,details=None,response_detail=None):
    await db.rollback();event=await append_security_event(db,event_type,"HIGH",node,details or {});await ws_manager.broadcast_event("security.event",row(event));raise HTTPException(status_code,response_detail or event_type)
@router.get("/status")
async def status():return {"signed_telemetry":"CONFIGURED" if keys() else "NOT_CONFIGURED","key_storage":"SERVER_ENVIRONMENT","replay_protection":"ACTIVE","audit_chain":"ACTIVE"}
@router.post("/telemetry/ingest")
async def ingest(envelope:dict=Body(...),db:AsyncSession=Depends(get_db)):
    node=envelope.get("node_id");nonce=envelope.get("nonce");signature=envelope.get("signature","");secret=keys().get(node)
    if not secret:await reject(db,"UNKNOWN_DEVICE",503,node,response_detail="DEVICE_KEY_NOT_CONFIGURED")
    unsigned={k:v for k,v in envelope.items() if k!="signature"};canonical=json.dumps(unsigned,sort_keys=True,separators=(",",":"));expected=hmac.new(secret.encode(),canonical.encode(),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,signature):await reject(db,"INVALID_SIGNATURE",401,node,{"nonce":nonce})
    if not isinstance(nonce,str) or not nonce or len(nonce)>128:await reject(db,"INVALID_NONCE",422,node)
    payload=dict(envelope.get("payload") or {})
    if payload.get("source_mode") not in (None,"REAL") or payload.get("is_simulation") is True:await reject(db,"PROVENANCE_CONFLICT",422,node,{"nonce":nonce})
    try:
        sent=datetime.fromisoformat(envelope["timestamp"].replace("Z","+00:00"));sent=sent if sent.tzinfo else sent.replace(tzinfo=timezone.utc)
    except Exception:await reject(db,"INVALID_TIMESTAMP",422,node,{"nonce":nonce})
    if abs((datetime.now(timezone.utc)-sent.astimezone(timezone.utc)).total_seconds())>300:await reject(db,"STALE_SIGNED_ENVELOPE",422,node,{"nonce":nonce})
    payload.update({"node_id":node,"timestamp":envelope["timestamp"],"source_mode":"REAL","is_simulation":False,"transport":"SIGNED_GATEWAY"})
    try:validated=TelemetryIngestPayload.model_validate(payload).model_dump(mode="json")
    except ValidationError:await reject(db,"INVALID_SIGNED_PAYLOAD",422,node,{"nonce":nonce})
    seen=(await db.execute(select(TelemetryNonce).where(TelemetryNonce.node_id==node,TelemetryNonce.nonce==nonce))).scalar_one_or_none()
    if seen:await reject(db,"REPLAY_DETECTED",409,node,{"nonce":nonce})
    sequence=int(validated["sequence"])
    reserved=(await db.execute(update(SecureDeviceState).where(SecureDeviceState.node_id==node,SecureDeviceState.last_sequence<sequence).values(last_sequence=sequence,updated_at=datetime.now(timezone.utc)))).rowcount
    if not reserved:
        if await db.get(SecureDeviceState,node):await reject(db,"SEQUENCE_REPLAY",409,node,{"nonce":nonce,"sequence":sequence})
        db.add(SecureDeviceState(node_id=node,last_sequence=sequence))
    db.add(TelemetryNonce(node_id=node,nonce=nonce,signature_fingerprint=hashlib.sha256(signature.encode()).hexdigest()))
    previous_cache=telemetry_service._last_sequence.get(node)
    try:
        await db.flush();result=await telemetry_service.ingest_packet(db,validated,"SIGNED_GATEWAY")
        if result.get("status")!="success":await reject(db,"SEQUENCE_REPLAY",409,node,{"nonce":nonce,"sequence":sequence})
    except IntegrityError:await reject(db,"REPLAY_DETECTED",409,node,{"nonce":nonce})
    except HTTPException:raise
    except Exception:
        if previous_cache is None:telemetry_service._last_sequence.pop(node,None)
        else:telemetry_service._last_sequence[node]=previous_cache
        await reject(db,"INVALID_SIGNED_PAYLOAD",422,node,{"nonce":nonce})
    event=await append_security_event(db,"SIGNED_TELEMETRY_ACCEPTED","INFO",node,{"nonce":nonce,"sequence":sequence});await ws_manager.broadcast_event("security.event",row(event));return {"security_state":"VERIFIED","telemetry":result}
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
