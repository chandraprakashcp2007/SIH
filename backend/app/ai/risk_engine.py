"""
PRAHARI-NET Hybrid Risk Engine
Coordinates Feature Extraction, Sensor Trust, Anomaly Detection, Multi-Sensor Fusion,
Explainability, and Predictive Trends into an authoritative operational risk score.
"""
from typing import Dict, Any, List, Optional
from backend.app.ai.trust import sensor_trust_engine
from backend.app.ai.features import feature_engine
from backend.app.ai.anomaly import anomaly_detector
from backend.app.ai.fusion import sensor_fusion_engine
from backend.app.ai.explainability import explainability_engine
from backend.app.ai.prediction import prediction_engine


class HybridRiskEngine:
    """Authoritative risk decision engine combining multi-sensor fusion with trust and explainability."""

    @staticmethod
    def get_risk_band(score: float) -> str:
        """Standard prototype risk band classifier."""
        if score >= 76.0:
            return "CRITICAL"
        elif score >= 51.0:
            return "WARNING"
        elif score >= 26.0:
            return "WATCH"
        return "NORMAL"

    def evaluate_node(
        self,
        node_id: str,
        current_metrics: Dict[str, Any],
        recent_history: List[Dict[str, Any]],
        is_simulation: bool = False
    ) -> Dict[str, Any]:
        """Dispatch evaluation to appropriate node processor."""
        if node_id == "JALA-01":
            return self.evaluate_jala(current_metrics, recent_history, is_simulation)
        elif node_id == "AGNI-02":
            return self.evaluate_agni(current_metrics, recent_history, is_simulation)
        elif node_id == "BHUMI-03":
            return self.evaluate_bhumi(current_metrics, recent_history, is_simulation)
        else:
            return self._fallback_evaluation(node_id, current_metrics, is_simulation)

    def evaluate_jala(
        self,
        metrics: Dict[str, Any],
        history: List[Dict[str, Any]],
        is_simulation: bool = False
    ) -> Dict[str, Any]:
        # 1. Sensor Trust
        trust_scores, trust_anomalies = sensor_trust_engine.evaluate_node_trust("JALA-01", metrics, history)

        # 2. Features & Derivatives
        wl = float(metrics.get("water_level_cm", 30.0))
        derivatives = feature_engine.calculate_derivatives("water_level_cm", wl, history)
        trend_direction = feature_engine.compute_trend("water_level_cm", history, wl)

        # 3. Anomaly Detection
        metrics_with_deriv = metrics.copy()
        metrics_with_deriv["water_rise_rate_cm_min"] = derivatives["velocity_per_min"]
        metrics_with_deriv["water_rise_acceleration"] = derivatives["acceleration"]
        anomaly_score = anomaly_detector.score_telemetry("JALA-01", metrics_with_deriv)

        # 4. Multi-Sensor Fusion
        fused_score, factors = sensor_fusion_engine.fuse_jala(metrics, trust_scores, derivatives)

        # Adjust score slightly if anomaly detector caught unusual pattern
        risk_score = round(min(100.0, max(0.0, fused_score + (anomaly_score * 8.0))), 1)
        risk_band = self.get_risk_band(risk_score)

        # 5. Confidence Calculation
        avg_trust = sum(trust_scores.values()) / max(1, len(trust_scores))
        confidence = round(min(100.0, max(30.0, (avg_trust * 0.8) + ((1.0 - abs(anomaly_score - 0.5)) * 20.0))), 1)

        # 6. Predictions
        crossing_time = prediction_engine.estimate_flood_threshold(
            current_level_cm=wl,
            velocity_cm_min=derivatives["velocity_per_min"],
            acceleration_cm_min2=derivatives["acceleration"],
            warning_threshold_cm=180.0
        )

        # 7. Explainability
        explanation = explainability_engine.generate_explanation(
            node_id="JALA-01",
            risk_score=risk_score,
            risk_band=risk_band,
            confidence=confidence,
            factors=factors,
            trust=trust_scores,
            anomalies=trust_anomalies
        )

        model_source = "SIMULATION" if is_simulation else "RULE_FUSION"

        return {
            "node_id": "JALA-01",
            "risk_score": risk_score,
            "risk_band": risk_band,
            "confidence": confidence,
            "anomaly_score": anomaly_score,
            "sensor_trust": trust_scores,
            "contributing_factors": factors,
            "human_explanation": explanation["human_readable"],
            "machine_explanation": explanation["machine_readable"],
            "recommended_action": explanation["recommended_action"],
            "model_source": model_source,
            "estimated_crossing_time": crossing_time,
            "risk_trend": trend_direction,
            "derivatives": derivatives
        }

    def evaluate_agni(
        self,
        metrics: Dict[str, Any],
        history: List[Dict[str, Any]],
        is_simulation: bool = False
    ) -> Dict[str, Any]:
        # 1. Sensor Trust
        trust_scores, trust_anomalies = sensor_trust_engine.evaluate_node_trust("AGNI-02", metrics, history)

        # 2. Features & Trends
        mq2 = float(metrics.get("mq2_raw", 120.0))
        trend_direction = feature_engine.compute_trend("mq2_raw", history, mq2)

        # 3. Anomaly Detection
        anomaly_score = anomaly_detector.score_telemetry("AGNI-02", metrics)

        # 4. Multi-Sensor Fusion
        fused_score, factors = sensor_fusion_engine.fuse_agni(metrics, trust_scores)
        risk_score = round(min(100.0, max(0.0, fused_score + (anomaly_score * 5.0))), 1)
        risk_band = self.get_risk_band(risk_score)

        # 5. Confidence
        avg_trust = sum(trust_scores.values()) / max(1, len(trust_scores))
        confidence = round(min(100.0, max(30.0, (avg_trust * 0.85) + 10.0)), 1)

        # 6. Explainability
        explanation = explainability_engine.generate_explanation(
            node_id="AGNI-02",
            risk_score=risk_score,
            risk_band=risk_band,
            confidence=confidence,
            factors=factors,
            trust=trust_scores,
            anomalies=trust_anomalies
        )

        model_source = "SIMULATION" if is_simulation else "RULE_FUSION"

        return {
            "node_id": "AGNI-02",
            "risk_score": risk_score,
            "risk_band": risk_band,
            "confidence": confidence,
            "anomaly_score": anomaly_score,
            "sensor_trust": trust_scores,
            "contributing_factors": factors,
            "human_explanation": explanation["human_readable"],
            "machine_explanation": explanation["machine_readable"],
            "recommended_action": explanation["recommended_action"],
            "model_source": model_source,
            "estimated_crossing_time": None,
            "risk_trend": trend_direction
        }

    def evaluate_bhumi(
        self,
        metrics: Dict[str, Any],
        history: List[Dict[str, Any]],
        is_simulation: bool = False
    ) -> Dict[str, Any]:
        # 1. Sensor Trust
        trust_scores, trust_anomalies = sensor_trust_engine.evaluate_node_trust("BHUMI-03", metrics, history)

        # 2. Features & Trends
        tilt = float(metrics.get("tilt_delta_deg", 0.0))
        trend_direction = feature_engine.compute_trend("tilt_delta_deg", history, tilt)

        # 3. Anomaly Detection
        anomaly_score = anomaly_detector.score_telemetry("BHUMI-03", metrics)

        # 4. Multi-Sensor Fusion
        fused_score, factors = sensor_fusion_engine.fuse_bhumi(metrics, trust_scores)
        risk_score = round(min(100.0, max(0.0, fused_score + (anomaly_score * 6.0))), 1)
        risk_band = self.get_risk_band(risk_score)

        # 5. Confidence
        avg_trust = sum(trust_scores.values()) / max(1, len(trust_scores))
        confidence = round(min(100.0, max(30.0, (avg_trust * 0.85) + 10.0)), 1)

        # 6. Explainability
        explanation = explainability_engine.generate_explanation(
            node_id="BHUMI-03",
            risk_score=risk_score,
            risk_band=risk_band,
            confidence=confidence,
            factors=factors,
            trust=trust_scores,
            anomalies=trust_anomalies
        )

        model_source = "SIMULATION" if is_simulation else "RULE_FUSION"

        return {
            "node_id": "BHUMI-03",
            "risk_score": risk_score,
            "risk_band": risk_band,
            "confidence": confidence,
            "anomaly_score": anomaly_score,
            "sensor_trust": trust_scores,
            "contributing_factors": factors,
            "human_explanation": explanation["human_readable"],
            "machine_explanation": explanation["machine_readable"],
            "recommended_action": explanation["recommended_action"],
            "model_source": model_source,
            "estimated_crossing_time": None,
            "risk_trend": trend_direction
        }

    def _fallback_evaluation(self, node_id: str, metrics: Dict[str, Any], is_simulation: bool) -> Dict[str, Any]:
        return {
            "node_id": node_id,
            "risk_score": 10.0,
            "risk_band": "NORMAL",
            "confidence": 90.0,
            "anomaly_score": 0.0,
            "sensor_trust": {"generic_sensor": 95.0},
            "contributing_factors": [],
            "human_explanation": "Normal baseline monitoring.",
            "machine_explanation": {},
            "recommended_action": "Routine observation.",
            "model_source": "SIMULATION" if is_simulation else "RULE_FUSION",
            "estimated_crossing_time": None,
            "risk_trend": "STABLE"
        }


risk_engine = HybridRiskEngine()
