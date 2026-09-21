"""
PRAHARI-NET Lightweight Anomaly Detection Engine
Uses scikit-learn IsolationForest to identify multivariate outliers.
"""
import numpy as np
from typing import Dict, Any, List
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    """
    Multivariate anomaly detector with baseline nominal data initialization.
    Computes an anomaly_score in [0.0, 1.0].
    """

    def __init__(self):
        self.models: Dict[str, IsolationForest] = {}
        self._initialize_baselines()

    def _initialize_baselines(self):
        """Fit lightweight IsolationForest models with synthetic nominal environmental baselines."""
        rng = np.random.RandomState(42)

        # JALA baseline: [water_level_cm, rise_rate, rain_intensity]
        # Normal ranges: water 20-45 cm, rate -1 to +1 cm/min, rain 0-10 mm/hr
        n_samples = 300
        jala_nominal = np.column_stack([
            rng.uniform(20.0, 45.0, n_samples),
            rng.uniform(-1.0, 1.0, n_samples),
            rng.uniform(0.0, 8.0, n_samples)
        ])
        model_jala = IsolationForest(n_estimators=50, contamination=0.05, random_state=42)
        model_jala.fit(jala_nominal)
        self.models["JALA-01"] = model_jala

        # AGNI baseline: [mq2_raw, mq135_raw, temp_c]
        # Normal ranges: mq2 80-180, mq135 90-200, temp 22-34 C
        agni_nominal = np.column_stack([
            rng.uniform(80.0, 180.0, n_samples),
            rng.uniform(90.0, 200.0, n_samples),
            rng.uniform(22.0, 34.0, n_samples)
        ])
        model_agni = IsolationForest(n_estimators=50, contamination=0.05, random_state=42)
        model_agni.fit(agni_nominal)
        self.models["AGNI-02"] = model_agni

        # BHUMI baseline: [soil_moisture_upper, tilt_delta, vibration_rms]
        # Normal ranges: moisture 20-45%, tilt 0-1 deg, vib 0-1.5
        bhumi_nominal = np.column_stack([
            rng.uniform(20.0, 45.0, n_samples),
            rng.uniform(0.0, 1.2, n_samples),
            rng.uniform(0.0, 1.5, n_samples)
        ])
        model_bhumi = IsolationForest(n_estimators=50, contamination=0.05, random_state=42)
        model_bhumi.fit(bhumi_nominal)
        self.models["BHUMI-03"] = model_bhumi

    def score_telemetry(self, node_id: str, metrics: Dict[str, Any]) -> float:
        """
        Evaluate anomaly score for current node telemetry.
        Returns float in range [0.0, 1.0] where 1.0 is extreme anomaly.
        """
        if node_id not in self.models:
            return 0.0

        try:
            if node_id == "JALA-01":
                feat = np.array([[
                    float(metrics.get("water_level_cm", 30.0)),
                    float(metrics.get("water_rise_rate_cm_min", 0.0)),
                    float(metrics.get("rain_intensity", 0.0))
                ]])
            elif node_id == "AGNI-02":
                feat = np.array([[
                    float(metrics.get("mq2_raw", 120.0)),
                    float(metrics.get("mq135_raw", 130.0)),
                    float(metrics.get("temperature_c", 27.0))
                ]])
            elif node_id == "BHUMI-03":
                feat = np.array([[
                    float(metrics.get("soil_moisture_upper_pct", 30.0)),
                    float(metrics.get("tilt_delta_deg", 0.2)),
                    float(metrics.get("vibration_rms", 0.5))
                ]])
            else:
                return 0.0

            # decision_function gives signed distance to separating hyperplane (negative = anomaly)
            score_raw = self.models[node_id].decision_function(feat)[0]
            # Map raw score [-0.5, 0.5] smoothly to [1.0, 0.0]
            anomaly_prob = 1.0 / (1.0 + np.exp(score_raw * 10.0))
            return float(np.clip(round(anomaly_prob, 3), 0.0, 1.0))
        except Exception:
            return 0.0


anomaly_detector = AnomalyDetector()
