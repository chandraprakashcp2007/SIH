from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.api.auth import require_roles
from backend.app.models.audit import AuditLog, SystemSetting

router = APIRouter(prefix="/calibration", tags=["Calibration"])

DEFAULT_CALIBRATION = {
    "JALA-01": {"water_level_offset_cm": 0.0, "rain_gauge_factor": 1.0},
    "AGNI-02": {"mq2_baseline": 115.0, "mq135_baseline": 128.0, "thermal_offset_c": 0.0},
    "BHUMI-03": {"tilt_x_zero_deg": 0.35, "tilt_y_zero_deg": -0.22, "vibration_zero": 0.45},
    "VAYU-04": {
        "pm2_5_offset": 0.0,
        "pm10_offset": 0.0,
        "co_offset_ppm": 0.0
    },
    "AKASHA-05": {
        "pressure_offset_hpa": 0.0,
        "rain_factor": 1.0,
        "wind_factor": 1.0
    },
}


class CalibrationUpdate(BaseModel):
    node_id: str
    values: Dict[str, float]


@router.get("")
async def get_calibration(db: AsyncSession = Depends(get_db)):
    nodes = {key: dict(value) for key, value in DEFAULT_CALIBRATION.items()}
    result = await db.execute(select(SystemSetting).where(SystemSetting.category == "CALIBRATION"))
    for setting in result.scalars().all():
        if setting.key in nodes and isinstance(setting.value_json, dict):
            nodes[setting.key].update(setting.value_json)
    return {"nodes": nodes, "source": "PERSISTED_WITH_SAFE_DEFAULTS", "updated_at": datetime.now(timezone.utc).isoformat()}


@router.put("")
async def update_calibration(
    req: CalibrationUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_roles("ADMIN")),
):
    if req.node_id not in DEFAULT_CALIBRATION:
        raise HTTPException(status_code=404, detail="Unknown node")
    allowed = set(DEFAULT_CALIBRATION[req.node_id])
    if not req.values or set(req.values) - allowed:
        raise HTTPException(status_code=422, detail=f"Allowed calibration keys: {sorted(allowed)}")
    result = await db.execute(select(SystemSetting).where(SystemSetting.key == req.node_id, SystemSetting.category == "CALIBRATION"))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value_json = req.values
    else:
        db.add(SystemSetting(key=req.node_id, category="CALIBRATION", value_json=req.values))
    db.add(AuditLog(action="CALIBRATION_UPDATED", category="CALIBRATION", component="calibration", message=f"Calibration updated for {req.node_id}", details={"values": req.values}))
    await db.commit()
    return {"status": "success", "node_id": req.node_id, "values": req.values}
