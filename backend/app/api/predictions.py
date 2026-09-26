"""
Predictions and Hazard Forecasting API Router
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.risk import RiskAssessment
from backend.app.models.telemetry import TelemetryRecord
from backend.app.ai.prediction import prediction_engine

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.get("")
async def get_predictions(db: AsyncSession = Depends(get_db)):
    """Retrieve grounded predictive trend indicators for each hazard node."""
    nodes = [
        {"id": "JALA-01", "name": "Brahmaputra Flood Basin", "hazard": "FLOOD"},
        {"id": "AGNI-02", "name": "Similipal Forest Perimeter", "hazard": "FIRE"},
        {"id": "BHUMI-03", "name": "BHUMI Slope Intelligence", "hazard": "LANDSLIDE"},
        {"id": "VAYU-04", "name": "VAYU Air Intelligence", "hazard": "AIR_QUALITY"},
        {"id": "AKASHA-05", "name": "AKASHA Atmospheric Intelligence", "hazard": "EXTREME_WEATHER"}
    ]
    results = []

    for n in nodes:
        nid = n["id"]
        # Fetch last 10 risk assessments
        res = await db.execute(
            select(RiskAssessment)
            .where(RiskAssessment.node_id == nid)
            .order_by(desc(RiskAssessment.timestamp))
            .limit(10)
        )
        risks = res.scalars().all()
        risks.reverse()

        if not risks or len(risks) < 2:
            results.append({
                "node_id": nid,
                "node_name": n["name"],
                "hazard": n["hazard"],
                "status": "INSUFFICIENT DATA",
                "current_risk": 0.0,
                "trend_direction": "STABLE",
                "projected_5min_change": 0.0,
                "prediction_confidence": 0.0,
                "threshold_crossing_window": "INSUFFICIENT DATA",
                "model_source": "RULE_FUSION",
                "last_execution": None
            })
            continue

        latest = risks[-1]
        history_scores = [r.risk_score for r in risks]
        trend_dir = latest.risk_trend or "STABLE"

        projection = prediction_engine.calculate_risk_projection(
            current_risk=latest.risk_score,
            history=history_scores,
            trend_direction=trend_dir
        )

        results.append({
            "node_id": nid,
            "node_name": n["name"],
            "hazard": n["hazard"],
            "status": "ACTIVE",
            "current_risk": latest.risk_score,
            "risk_band": latest.risk_band,
            "trend_direction": projection["direction"],
            "projected_5min_change": projection["projected_5min_change"],
            "prediction_confidence": projection["projection_confidence"],
            "threshold_crossing_window": latest.estimated_crossing_time or "NO THRESHOLD CROSSING DETECTED",
            "model_source": latest.model_source,
            "last_execution": latest.timestamp.isoformat()
        })

    return results
