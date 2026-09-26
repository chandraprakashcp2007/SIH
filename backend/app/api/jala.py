from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.jala_topology import DownstreamThreatAssessment, RiverTopologyDataset
from backend.app.models.telemetry import TelemetryRecord
from backend.app.websocket.manager import ws_manager

router = APIRouter(prefix="/jala", tags=["JALA Intelligence"])


def _row(item):
    return {column.name: getattr(item, column.name) for column in item.__table__.columns}


@router.get("/topology")
async def topology(db: AsyncSession = Depends(get_db)):
    dataset = (await db.execute(select(RiverTopologyDataset).order_by(desc(RiverTopologyDataset.imported_at)).limit(1))).scalar_one_or_none()
    if not dataset:
        return {"status": "NOT_CONFIGURED", "dataset": None, "reaches": [], "provenance": "EXTERNAL_DATA",
                "reason": "No authoritative river topology dataset has been imported and validated."}
    return {"status": dataset.status, "dataset": _row(dataset), "reaches": dataset.reaches,
            "provenance": dataset.provenance, "reason": dataset.validation.get("reason")}


@router.post("/downstream-threats/evaluate")
async def evaluate_downstream_threats(db: AsyncSession = Depends(get_db)):
    dataset = (await db.execute(select(RiverTopologyDataset).where(RiverTopologyDataset.status == "VALIDATED").order_by(desc(RiverTopologyDataset.imported_at)).limit(1))).scalar_one_or_none()
    telemetry = (await db.execute(select(TelemetryRecord).where(TelemetryRecord.node_id == "JALA-01").order_by(desc(TelemetryRecord.timestamp)).limit(1))).scalar_one_or_none()
    if not dataset:
        assessment = DownstreamThreatAssessment(
            source_node_id="JALA-01", status="NOT_CONFIGURED", threatened_reaches=[],
            travel_time_minutes=None, time_to_impact_state="UNAVAILABLE", method="TOPOLOGY_REQUIRED",
            provenance=telemetry.source_mode if telemetry else "SIMULATION",
            reason="A validated topology and travel-time basis are required; downstream time-to-impact is unavailable.",
        )
    else:
        # Import validation requires each usable reach to carry a documented travel-time basis.
        usable = [reach for reach in dataset.reaches if reach.get("travel_time_validated") and reach.get("travel_time_minutes") is not None]
        travel = min((float(reach["travel_time_minutes"]) for reach in usable), default=None)
        assessment = DownstreamThreatAssessment(
            source_node_id="JALA-01", topology_dataset_id=dataset.id,
            status="AVAILABLE" if usable else "INSUFFICIENT_PARAMETERS", threatened_reaches=usable,
            travel_time_minutes=travel, time_to_impact_state="AVAILABLE" if travel is not None else "UNAVAILABLE",
            method="VALIDATED_REACH_TRAVEL_TIME", provenance=dataset.provenance,
            reason="Minimum validated reach travel time." if travel is not None else "Validated travel-time parameters are absent from configured reaches.",
        )
    db.add(assessment)
    await db.commit()
    result = _row(assessment)
    await ws_manager.broadcast_event("jala.downstream_threat.updated", result)
    return result


@router.get("/downstream-threats")
async def downstream_threats(limit: int = 20, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(DownstreamThreatAssessment).order_by(desc(DownstreamThreatAssessment.evaluated_at)).limit(min(max(limit, 1), 100)))).scalars()
    return [_row(row) for row in rows]
