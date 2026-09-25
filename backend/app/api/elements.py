from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.domain.registry import DOMAIN_REGISTRY
from backend.app.models.telemetry import TelemetryRecord


router = APIRouter(prefix="/elements", tags=["Pancha Bhootha"])


@router.get("")
async def list_elements(db: AsyncSession = Depends(get_db)):
    result = []
    for definition in DOMAIN_REGISTRY.values():
        latest = None
        source_mode = definition.default_source_mode.value
        if definition.risk_engine_available:
            latest = (await db.execute(
                select(TelemetryRecord)
                .where(TelemetryRecord.node_id == definition.domain_id)
                .order_by(desc(TelemetryRecord.server_received_at))
                .limit(1)
            )).scalar_one_or_none()
            if latest:
                source_mode = latest.source_mode
        result.append({
            "domain_id": definition.domain_id,
            "display_name": definition.display_name,
            "element": definition.element,
            "primary_hazards": list(definition.primary_hazards),
            "supported_metrics": list(definition.supported_metrics),
            "source_mode": source_mode,
            "hardware_state": definition.hardware_state,
            "risk_engine_state": "AVAILABLE" if definition.risk_engine_available else "NOT_IMPLEMENTED",
            "description": definition.description,
            "latest_update": latest.server_received_at.isoformat() if latest else None,
            "hardware_profile": definition.hardware_profile.to_dict(),
        })
    return result
