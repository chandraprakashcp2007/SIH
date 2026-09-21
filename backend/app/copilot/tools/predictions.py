"""
Copilot Predictions Tool
Queries hazard forecast trends and projected threshold crossing times.
"""
from typing import Dict, Any, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.risk import RiskAssessment
from backend.app.ai.prediction import prediction_engine


async def get_predictions(db: AsyncSession) -> List[Dict[str, Any]]:
    """Retrieve predictive hazard trajectory and threshold crossing estimates."""
    nodes = [
        {"id": "JALA-01", "name": "Brahmaputra Flood Basin", "hazard": "FLOOD"},
        {"id": "AGNI-02", "name": "Similipal Forest Perimeter", "hazard": "FIRE"},
        {"id": "BHUMI-03", "name": "NH-58 Landslide Ghat", "hazard": "LANDSLIDE"}
    ]
    results = []

    for n in nodes:
        nid = n["id"]
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
                "hazard": n["hazard"],
                "status": "NOMINAL",
                "current_risk": 0.0,
                "projected_change": 0.0,
                "crossing_window": "NO THRESHOLD CROSSING DETECTED"
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
            "hazard": n["hazard"],
            "current_risk": latest.risk_score,
            "risk_band": latest.risk_band,
            "trend_direction": projection["direction"],
            "projected_5min_change": projection["projected_5min_change"],
            "crossing_window": latest.estimated_crossing_time or "NO THRESHOLD CROSSING DETECTED",
            "model_source": latest.model_source
        })

    return results
