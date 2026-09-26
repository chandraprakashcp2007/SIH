from fastapi import APIRouter,Body,Depends,HTTPException
from sqlalchemy import desc,select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.alerts import Alert
from backend.app.models.cap import CAPExport,DeliveryAttempt
from backend.app.services.cap_service import build_cap
from backend.app.websocket.manager import ws_manager
router=APIRouter(prefix="/cap",tags=["CAP Interoperability"])
def row(x):return {c.name:getattr(x,c.name) for c in x.__table__.columns}
async def alert(db,id):
    value=(await db.execute(select(Alert).where(Alert.id==id))).scalar_one_or_none()
    if not value:raise HTTPException(404,"Alert not found")
    return value
@router.get("/status")
async def status():
    return {"export":"AVAILABLE","label":"CAP-compatible interoperability export","official_integration":"NOT_CONFIGURED","channels":[{"channel":x,"state":"NOT_CONFIGURED"} for x in ("SMS","CELL_BROADCAST","SACHET","EMAIL")]}
@router.post("/alerts/{alert_id}/export")
async def export(alert_id:str,payload:dict=Body(default={}),db:AsyncSession=Depends(get_db)):
    item=await alert(db,alert_id);languages=payload.get("languages") or ["en-IN"];identifier,xml,provenance=build_cap(item,languages);record=CAPExport(alert_id=alert_id,identifier=identifier,lifecycle=item.state,languages=languages,xml=xml,provenance=provenance,validation_state="VALID");db.add(record);await db.commit();result=row(record);result["label"]="CAP-compatible interoperability export";await ws_manager.broadcast_event("cap.exported",{"id":record.id,"alert_id":alert_id});return result
@router.post("/alerts/{alert_id}/deliver")
async def deliver(alert_id:str,payload:dict=Body(...),db:AsyncSession=Depends(get_db)):
    await alert(db,alert_id);record=DeliveryAttempt(alert_id=alert_id,channel=payload.get("channel","UNKNOWN"),state="NOT_CONFIGURED",provider_message_id=None,delivered_at=None,reason="No authorized delivery provider credentials or deployment permission are configured.");db.add(record);await db.commit();result=row(record);await ws_manager.broadcast_event("delivery.state.changed",result);return result
@router.get("/exports")
async def exports(db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(CAPExport).order_by(desc(CAPExport.created_at)).limit(50))).scalars();return [row(x) for x in rows]
@router.get("/deliveries")
async def deliveries(db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(DeliveryAttempt).order_by(desc(DeliveryAttempt.requested_at)).limit(50))).scalars();return [row(x) for x in rows]
