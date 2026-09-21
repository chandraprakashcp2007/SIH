"""
PRAHARI-NET Feature Engineering Engine
Calculates rolling metrics, rates of change, acceleration, and trend indicators.
"""
from typing import Dict, Any, List


class FeatureEngine:
    """Computes operational features and numerical derivatives from telemetry streams."""

    @staticmethod
    def calculate_derivatives(
        metric: str,
        current_val: float,
        history: List[Dict[str, Any]],
        dt_seconds: float = 2.0
    ) -> Dict[str, float]:
        """
        Compute velocity (rate of change / min) and acceleration.
        Returns: { 'velocity_per_min': float, 'acceleration': float, 'rolling_mean': float }
        """
        if not history:
            return {
                "velocity_per_min": 0.0,
                "acceleration": 0.0,
                "rolling_mean": current_val
            }

        # Extract last values
        recent_vals = [float(h.get(metric, current_val)) for h in history[-5:]]
        recent_vals.append(current_val)

        rolling_mean = sum(recent_vals) / len(recent_vals)

        # 1st derivative (velocity per minute)
        prev_val = float(history[-1].get(metric, current_val))
        delta = current_val - prev_val
        velocity_per_min = (delta / dt_seconds) * 60.0

        # 2nd derivative (acceleration)
        prev_velocity = 0.0
        if len(history) >= 2:
            prev_2 = float(history[-2].get(metric, prev_val))
            prev_delta = prev_val - prev_2
            prev_velocity = (prev_delta / dt_seconds) * 60.0
        
        acceleration = (velocity_per_min - prev_velocity) / dt_seconds

        return {
            "velocity_per_min": round(velocity_per_min, 2),
            "acceleration": round(acceleration, 3),
            "rolling_mean": round(rolling_mean, 2)
        }

    @staticmethod
    def compute_trend(metric: str, history: List[Dict[str, Any]], current_val: float) -> str:
        """
        Determine operational trend direction:
        STABLE, RISING, RAPIDLY_RISING, FALLING
        """
        if len(history) < 3:
            return "STABLE"

        recent = [float(h.get(metric, current_val)) for h in history[-3:]]
        delta_total = current_val - recent[0]

        if delta_total > 15.0:
            return "RAPIDLY_RISING"
        elif delta_total > 3.0:
            return "RISING"
        elif delta_total < -3.0:
            return "FALLING"
        else:
            return "STABLE"


feature_engine = FeatureEngine()
