from fastapi import APIRouter,Depends
from sqlalchemy import desc,select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.digital_twin import DigitalTwinSnapshot
from backend.app.models.geospatial import GeoDataset
from backend.app.models.nodes import Node
from backend.app.models.risk import RiskAssessment
from backend.app.models.telemetry import TelemetryRecord
from backend.app.websocket.manager import ws_manager

router=APIRouter(prefix="/digital-twin",tags=["Digital Twin"])
def row(x): return {c.name:getattr(x,c.name) for c in x.__table__.columns}

@router.post("/refresh")
async def refresh(db:AsyncSession=Depends(get_db)):
    nodes=list((await db.execute(select(Node))).scalars()); datasets=list((await db.execute(select(GeoDataset))).scalars())
    out=[]
    for node in nodes:
        risk=(await db.execute(select(RiskAssessment).where(RiskAssessment.node_id==node.id).order_by(desc(RiskAssessment.timestamp)).limit(1))).scalar_one_or_none()
        tele=(await db.execute(select(TelemetryRecord).where(TelemetryRecord.node_id==node.id).order_by(desc(TelemetryRecord.timestamp)).limit(1))).scalar_one_or_none()
        missing=[d.name for d in datasets if (d.domain or "").lower() in {node.id.split('-')[0].lower(),"all"} and d.status!="AVAILABLE"]
        if not missing: missing=["Validated hazard-boundary model is not configured"]
        confidence=float(risk.confidence if risk else 0); provenance=tele.source_mode if tele else node.source_mode
        snap=DigitalTwinSnapshot(node_id=node.id,observed_location={"type":"Point","coordinates":[node.longitude,node.latitude]},hazard_boundary=None,uncertainty_boundary=None,confidence=confidence,uncertainty=round(100-confidence,2),blind_spots=missing,provenance=provenance if provenance in {"REAL","SIMULATION","EXTERNAL_DATA","MODEL"} else "SIMULATION",boundary_state="NOT_CONFIGURED",explanation="Observed node location is available; hazard and uncertainty boundaries require validated spatial models and authoritative layers.")
        db.add(snap);out.append(snap)
    await db.commit(); result=[row(x) for x in out]; await ws_manager.broadcast_event("digital_twin.updated",{"snapshots":result}); return result

@router.get("")
async def get_twins(db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(DigitalTwinSnapshot).order_by(desc(DigitalTwinSnapshot.captured_at)).limit(5))).scalars(); return [row(x) for x in rows]
