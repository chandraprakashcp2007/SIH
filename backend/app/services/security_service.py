import asyncio,hashlib,json
from datetime import datetime,timezone
from sqlalchemy import desc,select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.security import SecurityEvent
ZERO="0"*64
_audit_append_lock=asyncio.Lock()
async def append_security_event(db:AsyncSession,event_type:str,severity:str,node_id:str|None,details:dict):
    # Serialize append + commit so two requests in this process cannot select
    # the same predecessor and fork the audit chain.
    async with _audit_append_lock:
        previous=(await db.execute(select(SecurityEvent).order_by(desc(SecurityEvent.created_at),desc(SecurityEvent.id)).limit(1))).scalar_one_or_none();previous_hash=previous.event_hash if previous else ZERO
        created=datetime.now(timezone.utc);material=json.dumps({"event_type":event_type,"severity":severity,"node_id":node_id,"details":details,"previous_hash":previous_hash,"created_at":created.isoformat()},sort_keys=True,separators=(",",":"));event_hash=hashlib.sha256(material.encode()).hexdigest()
        item=SecurityEvent(event_type=event_type,severity=severity,node_id=node_id,details=details,previous_hash=previous_hash,event_hash=event_hash,created_at=created);db.add(item);await db.commit();return item
def expected_hash(item):
    material=json.dumps({"event_type":item.event_type,"severity":item.severity,"node_id":item.node_id,"details":item.details,"previous_hash":item.previous_hash,"created_at":item.created_at.replace(tzinfo=timezone.utc).isoformat()},sort_keys=True,separators=(",",":"));return hashlib.sha256(material.encode()).hexdigest()
