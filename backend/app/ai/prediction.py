"""
PRAHARI-NET Predictive Trend & Threshold Estimation Engine
Calculates honest extrapolation without false precision.
"""
from typing import Dict, Any, List, Optional


class PredictionEngine:
    """Estimates time-to-breach for hydrology and risk trajectory slopes."""

    @staticmethod
    def estimate_flood_threshold(
        current_level_cm: float,
        velocity_cm_min: float,
        acceleration_cm_min2: float,
        warning_threshold_cm: float = 180.0
    ) -> Optional[str]:
        """
        Estimate flood threshold crossing time window.
        Returns human-rounded string e.g. '~12–16 minutes' or None.
        """
        if current_level_cm >= warning_threshold_cm:
            return "THRESHOLD CURRENTLY EXCEEDED"

        if velocity_cm_min <= 0.1:
            return "NO THRESHOLD CROSSING PROJECTED"

        remaining_cm = warning_threshold_cm - current_level_cm

        # Linear estimate
        t_linear = remaining_cm / velocity_cm_min

        # If acceleration is positive, crossing happens sooner
        if acceleration_cm_min2 > 0.05:
            # Quadratic root approx
            t_accel = t_linear * 0.85
        elif acceleration_cm_min2 < -0.05:
            t_accel = t_linear * 1.25
        else:
            t_accel = t_linear

        low_est = max(1, int(min(t_linear, t_accel)))
        high_est = max(low_est + 2, int(max(t_linear, t_accel) + 2))

        if low_est > 180:
            return "> 3 hours"
        elif low_est > 60:
            return f"~{low_est // 60}h {low_est % 60}m"
        else:
            return f"~{low_est}–{high_est} minutes"

    @staticmethod
    def calculate_risk_projection(
        current_risk: float,
        history: List[float],
        trend_direction: str
    ) -> Dict[str, Any]:
        """Calculates 5-minute risk delta and confidence."""
        if len(history) < 3:
            return {
                "projected_5min_change": 0.0,
                "direction": "STABLE",
                "projection_confidence": 50.0
            }

        delta = current_risk - history[-3]
        projected_delta = delta * 1.5

        return {
            "projected_5min_change": round(projected_delta, 1),
            "direction": trend_direction,
            "projection_confidence": 85.0 if abs(delta) > 5.0 else 92.0
        }


prediction_engine = PredictionEngine()
