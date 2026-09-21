"""
Settings & Thresholds Configuration API Router
"""
from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.audit import SystemSetting, AuditLog

router = APIRouter(prefix="/settings", tags=["Settings"])

DEFAULT_SETTINGS = {
    "risk_bands": {
        "normal_max": 25,
        "watch_max": 50,
        "warning_max": 75,
        "critical_max": 100
    },
    "jala_thresholds": {
        "watch_level_cm": 60.0,
        "warning_level_cm": 120.0,
        "critical_level_cm": 180.0,
        "critical_rise_rate_cm_min": 4.5,
        "torrential_rain_mm_hr": 40.0
    },
    "agni_thresholds": {
        "mq2_watch_raw": 300,
        "mq2_warning_raw": 600,
        "mq2_critical_raw": 850,
        "critical_temp_c": 50.0,
        "vision_confidence_threshold": 0.70
    },
    "bhumi_thresholds": {
        "soil_saturation_warning_pct": 70.0,
        "soil_saturation_critical_pct": 85.0,
        "tilt_delta_warning_deg": 1.5,
        "tilt_delta_critical_deg": 4.0,
        "vibration_rms_critical": 8.0
    },
    "audio": {
        "enabled": False,
        "volume": 80,
        "repeat_interval_sec": 5
    },
    "gateway": {
        "mode": "SIMULATOR",
        "port": "COM3",
        "baud": 115200,
        "poll_rate_sec": 2.0
    },
    "map": {
        "provider": "OPENSTREETMAP",
        "default_lat": 26.2006,
        "default_lng": 92.9376,
        "default_zoom": 11
    }
}


class SettingsUpdateRequest(BaseModel):
    settings: Dict[str, Any]


@router.get("")
async def get_settings(db: AsyncSession = Depends(get_db)):
    """Retrieve all configurable system settings."""
    res = await db.execute(select(SystemSetting))
    db_settings = res.scalars().all()
    current = DEFAULT_SETTINGS.copy()
    for s in db_settings:
        current[s.key] = s.value_json
    return current


@router.put("")
async def update_settings(req: SettingsUpdateRequest, db: AsyncSession = Depends(get_db)):
    """Update settings and persist to database."""
    for key, val in req.settings.items():
        res = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
        existing = res.scalar_one_or_none()
        if existing:
            existing.value_json = val
        else:
            db.add(SystemSetting(key=key, category="GENERAL", value_json=val))

    db.add(AuditLog(
        action="SETTINGS_UPDATED",
        category="SETTINGS",
        component="settings_service",
        message="System threshold configuration updated.",
        details={"keys_updated": list(req.settings.keys())}
    ))
    await db.commit()
    return {"status": "success", "message": "Settings persisted successfully."}


@router.post("/reset")
async def reset_settings(db: AsyncSession = Depends(get_db)):
    """Reset settings back to safe prototype defaults."""
    res = await db.execute(select(SystemSetting))
    db_settings = res.scalars().all()
    for s in db_settings:
        await db.delete(s)
    await db.commit()
    return {"status": "success", "settings": DEFAULT_SETTINGS}
