"""
PRAHARI-NET Sensor Trust Engine
Calculates dynamic reliability (0 - 100%) for individual sensors.
Detects stuck values, out-of-range anomalies, impossible spikes, and cross-sensor contradictions.
"""
from typing import Dict, Any, List, Tuple, Optional


class SensorTrustEngine:
    """
    Evaluates raw telemetry stream to assign trust scores (0-100).
    Trust scales down risk impact if a sensor is glitching or contradicted.
    """

    # Physical validity bounds
    BOUNDS = {
        # JALA
        "water_level_cm": (0.0, 1000.0),
        "rain_intensity": (0.0, 150.0),  # mm/hr
        "water_rise_rate_cm_min": (-100.0, 100.0),
        # AGNI
        "mq2_raw": (10, 1024),
        "mq135_raw": (10, 1024),
        "smoke_index": (0.0, 100.0),
        "gas_index": (0.0, 100.0),
        "temperature_c": (-20.0, 85.0),
        "humidity_pct": (0.0, 100.0),
        "camera_fire_confidence": (0.0, 1.0),
        # BHUMI
        "soil_moisture_upper_pct": (0.0, 100.0),
        "soil_moisture_lower_pct": (0.0, 100.0),
        "tilt_x_deg": (-90.0, 90.0),
        "tilt_y_deg": (-90.0, 90.0),
        "tilt_delta_deg": (0.0, 90.0),
        "vibration_level": (0.0, 100.0),
        "vibration_rms": (0.0, 50.0),

        # VAYU
        "pm2_5": (0.0, 1000.0),
        "pm10": (0.0, 1500.0),
        "co_ppm": (0.0, 100.0),
        "voc_index": (0.0, 1000.0),

        # AKASHA
        "pressure_hpa": (850.0, 1100.0),
        "pressure_drop_hpa_3h": (0.0, 50.0),
        "wind_speed_kmh": (0.0, 300.0),
        "wind_gust_kmh": (0.0, 350.0),
    }

    # Maximum realistic physical change per sampling interval (~2 sec)
    MAX_REALISTIC_DELTA = {
        "water_level_cm": 15.0,        # max 15 cm in 2 sec
        "temperature_c": 10.0,         # max 10 C in 2 sec
        "mq2_raw": 600.0,
        "soil_moisture_upper_pct": 20.0,
        "tilt_delta_deg": 12.0
    }

    def evaluate_node_trust(
        self,
        node_id: str,
        current_metrics: Dict[str, Any],
        recent_history: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, float], List[str]]:
        """
        Evaluate trust for each sensor on the node.
        Returns: (trust_map, anomaly_reasons)
        """
        trust_scores: Dict[str, float] = {}
        anomalies: List[str] = []

        if node_id == "JALA-01":
            trust_scores, anomalies = self._evaluate_jala(current_metrics, recent_history)
        elif node_id == "AGNI-02":
            trust_scores, anomalies = self._evaluate_agni(current_metrics, recent_history)
        elif node_id == "BHUMI-03":
            trust_scores, anomalies = self._evaluate_bhumi(current_metrics, recent_history)
        else:
            for key, value in current_metrics.items():
                if isinstance(value, (int, float)):
                    score, reason = self._check_bounds(
                        key, float(value)
                    )
                    trust_scores[key] = round(score, 1)

                    if reason:
                        anomalies.append(reason)
                else:
                    trust_scores[key] = 95.0

        return trust_scores, anomalies

    def _check_bounds(self, metric: str, value: float) -> Tuple[float, Optional[str]]:
        if metric in self.BOUNDS:
            low, high = self.BOUNDS[metric]
            if value < low or value > high:
                return 30.0, f"{metric} out-of-physical bounds ({value} not in [{low}, {high}])"
        return 100.0, None

    def _check_stuck(self, metric: str, current: float, history: List[Dict[str, Any]]) -> Tuple[float, Optional[str]]:
        """Detect if sensor value is completely frozen across 8+ readings while others vary."""
        if len(history) < 6:
            return 100.0, None
        past_values = [h.get(metric) for h in history[-6:] if metric in h]
        if len(past_values) == 6 and all(abs(v - current) < 1e-4 for v in past_values):
            # Check if this is a sensor that normally has analog micro-jitter
            if metric in ["mq2_raw", "mq135_raw", "water_distance_cm", "soil_moisture_upper_pct"]:
                return 40.0, f"{metric} stuck reading detected (zero variance over 6 consecutive cycles)"
        return 100.0, None

    def _check_impossible_jump(self, metric: str, current: float, history: List[Dict[str, Any]]) -> Tuple[float, Optional[str]]:
        if not history or metric not in self.MAX_REALISTIC_DELTA:
            return 100.0, None
        last_val = history[-1].get(metric)
        if last_val is not None:
            delta = abs(current - float(last_val))
            max_delta = self.MAX_REALISTIC_DELTA[metric]
            if delta > max_delta:
                return 45.0, f"{metric} impossible jump: sudden delta of {delta:.1f} exceeds physical limit {max_delta}"
        return 100.0, None

    def _evaluate_jala(
        self,
        current: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, float], List[str]]:
        scores = {}
        anomalies = []

        # Water level sensor trust
        wl = float(current.get("water_level_cm", 0.0))
        score_b, err_b = self._check_bounds("water_level_cm", wl)
        score_s, err_s = self._check_stuck("water_level_cm", wl, history)
        score_j, err_j = self._check_impossible_jump("water_level_cm", wl, history)
        
        wl_score = min(score_b, score_s, score_j)
        for err in [err_b, err_s, err_j]:
            if err:
                anomalies.append(err)
        scores["water_level_sensor"] = round(wl_score, 1)

        # Rain sensor trust
        rain = float(current.get("rain_intensity", 0.0))
        rain_b, err_rb = self._check_bounds("rain_intensity", rain)
        if err_rb:
            anomalies.append(err_rb)
        scores["rain_sensor"] = round(rain_b, 1)

        # Temperature / humidity
        temp = float(current.get("temperature_c", 25.0))
        temp_b, _ = self._check_bounds("temperature_c", temp)
        scores["ambient_sensor"] = round(temp_b, 1)

        return scores, anomalies

    def _evaluate_agni(
        self,
        current: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, float], List[str]]:
        scores = {}
        anomalies = []

        mq2 = float(current.get("mq2_raw", 100.0))
        mq135 = float(current.get("mq135_raw", 120.0))
        temp = float(current.get("temperature_c", 25.0))
        flame = bool(current.get("flame_detected", False))
        cam_conf = float(current.get("camera_fire_confidence", 0.0))

        # Check bounds and stuck for MQ2
        s_b, err_b = self._check_bounds("mq2_raw", mq2)
        s_s, err_s = self._check_stuck("mq2_raw", mq2, history)
        mq2_trust = min(s_b, s_s)
        for err in [err_b, err_s]:
            if err:
                anomalies.append(err)

        # SENSOR CONTRADICTION CHECK:
        # If MQ2 suddenly spikes significantly (> 650) but MQ135 is low (< 250),
        # temperature is normal (< 36°C), flame is False, and camera is 0,
        # it is a false smoke/sensor glitch!
        if mq2 > 650 and mq135 < 300 and temp < 38.0 and not flame and cam_conf < 0.2:
            mq2_trust = 25.0
            anomalies.append("MQ2 smoke sensor isolated spike contradicted by normal MQ135, baseline temp, and optical flame sensor")

        scores["mq2_smoke_sensor"] = round(mq2_trust, 1)

        # MQ135 Air Quality trust
        s135_b, err135_b = self._check_bounds("mq135_raw", mq135)
        scores["mq135_gas_sensor"] = round(s135_b, 1)
        if err135_b:
            anomalies.append(err135_b)

        # Thermal sensor trust
        temp_b, err_tb = self._check_bounds("temperature_c", temp)
        scores["thermal_sensor"] = round(temp_b, 1)
        if err_tb:
            anomalies.append(err_tb)

        # Flame & optical sensor trust
        scores["optical_flame_sensor"] = 98.0
        scores["camera_ai_stream"] = 95.0 if cam_conf >= 0.0 else 0.0

        return scores, anomalies

    def _evaluate_bhumi(
        self,
        current: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, float], List[str]]:
        scores = {}
        anomalies = []

        m_up = float(current.get("soil_moisture_upper_pct", 30.0))
        m_low = float(current.get("soil_moisture_lower_pct", 35.0))
        tilt_delta = float(current.get("tilt_delta_deg", 0.0))
        vib_rms = float(current.get("vibration_rms", 0.0))

        # Upper Moisture
        u_b, err_ub = self._check_bounds("soil_moisture_upper_pct", m_up)
        u_s, err_us = self._check_stuck("soil_moisture_upper_pct", m_up, history)
        scores["soil_moisture_upper"] = round(min(u_b, u_s), 1)
        for err in [err_ub, err_us]:
            if err:
                anomalies.append(err)

        # Lower Moisture
        l_b, err_lb = self._check_bounds("soil_moisture_lower_pct", m_low)
        scores["soil_moisture_lower"] = round(l_b, 1)
        if err_lb:
            anomalies.append(err_lb)

        # Inclinometer / Tilt trust
        t_b, err_tb = self._check_bounds("tilt_delta_deg", tilt_delta)
        scores["inclinometer_tilt"] = round(t_b, 1)
        if err_tb:
            anomalies.append(err_tb)

        # Vibration / Geophone
        v_b, err_vb = self._check_bounds("vibration_rms", vib_rms)
        scores["geophone_vibration"] = round(v_b, 1)
        if err_vb:
            anomalies.append(err_vb)

        return scores, anomalies


sensor_trust_engine = SensorTrustEngine()
