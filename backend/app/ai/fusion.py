"""
PRAHARI-NET Multi-Sensor Fusion Engine
Synthesizes multiple correlated telemetry streams into unified hazard indicators.
Incorporates sensor trust weights to prevent false-alarm single-sensor triggering.
"""
from typing import Dict, Any, List, Tuple


class SensorFusionEngine:
    """Combines heterogeneous physical sensor observations with trust-adjusted weights."""

    def fuse_jala(
        self,
        metrics: Dict[str, Any],
        trust: Dict[str, float],
        derivatives: Dict[str, float]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Fuse JALA Flood Metrics:
        Water level + rate of rise + acceleration + rainfall intensity.
        Returns: (fused_hazard_index 0-100, factor_breakdown)
        """
        wl = float(metrics.get("water_level_cm", 30.0))
        rain = float(metrics.get("rain_intensity", 0.0))
        velocity = derivatives.get("velocity_per_min", 0.0)
        if velocity == 0.0 and "water_rise_rate_cm_min" in metrics:
            velocity = float(metrics["water_rise_rate_cm_min"])

        accel = derivatives.get("acceleration", 0.0)
        if accel == 0.0 and "water_rise_acceleration" in metrics:
            accel = float(metrics["water_rise_acceleration"])

        wl_trust = trust.get("water_level_sensor", 100.0) / 100.0
        rain_trust = trust.get("rain_sensor", 100.0) / 100.0

        # Normalization to [0, 100] components
        wl_score = min(100.0, max(0.0, (wl / 200.0) * 100.0))
        vel_score = min(100.0, max(0.0, (velocity / 6.0) * 100.0)) if velocity > 0 else 0.0
        accel_score = min(100.0, max(0.0, (accel / 1.5) * 100.0)) if accel > 0 else 0.0
        rain_score = min(100.0, max(0.0, (rain / 50.0) * 100.0))

        # Trust weighting
        wl_effective = wl_score * wl_trust
        vel_effective = vel_score * wl_trust
        accel_effective = accel_score * wl_trust
        rain_effective = rain_score * rain_trust

        # If water level exceeds threshold (e.g. >180 cm) AND rise rate is positive, risk is Critical
        if wl >= 180.0 and velocity > 1.0:
            fused = 76.0 + (vel_effective * 0.15) + (rain_effective * 0.09)
        else:
            fused = (
                wl_effective * 0.40 +
                vel_effective * 0.30 +
                accel_effective * 0.15 +
                rain_effective * 0.15
            )

        factors = [
            {"factor": "Water Gauge Level", "weight": 0.40, "value": f"{wl:.1f} cm", "score": round(wl_score, 1)},
            {"factor": "Rate of Rise", "weight": 0.30, "value": f"{velocity:+.2f} cm/min", "score": round(vel_score, 1)},
            {"factor": "Rise Acceleration", "weight": 0.15, "value": f"{accel:+.3f} cm/min²", "score": round(accel_score, 1)},
            {"factor": "Rainfall Intensity", "weight": 0.15, "value": f"{rain:.1f} mm/h", "score": round(rain_score, 1)},
        ]

        return round(min(100.0, max(0.0, fused)), 1), factors

    def fuse_agni(
        self,
        metrics: Dict[str, Any],
        trust: Dict[str, float]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Fuse AGNI Fire Metrics:
        Smoke/Gas (MQ2+MQ135) + Thermal + Optical Flame + Visual AI stream.
        """
        mq2 = float(metrics.get("mq2_raw", 120.0))
        mq135 = float(metrics.get("mq135_raw", 130.0))
        temp = float(metrics.get("temperature_c", 26.0))
        flame = bool(metrics.get("flame_detected", False))
        cam_conf = float(metrics.get("camera_fire_confidence", 0.0))

        mq2_trust = trust.get("mq2_smoke_sensor", 100.0) / 100.0
        mq135_trust = trust.get("mq135_gas_sensor", 100.0) / 100.0
        temp_trust = trust.get("thermal_sensor", 100.0) / 100.0

        # Smoke index (MQ2 baseline ~100, saturated ~900)
        smoke_score = min(100.0, max(0.0, ((mq2 - 100) / 700.0) * 100.0))
        # Gas index (MQ135 baseline ~120, saturated ~800)
        gas_score = min(100.0, max(0.0, ((mq135 - 120) / 650.0) * 100.0))
        air_score = (smoke_score * 0.6 + gas_score * 0.4) * min(mq2_trust, mq135_trust)

        # Thermal score: ambient 25C -> 70C+
        temp_score = min(100.0, max(0.0, ((temp - 30.0) / 40.0) * 100.0)) * temp_trust
        
        # Flame optical detector
        flame_score = 100.0 if flame else 0.0
        
        # Visual AI
        cam_score = cam_conf * 100.0

        # Fusion: If flame OR high heat corroborates smoke, fire risk rises sharply
        # If smoke spikes alone with zero heat, zero flame, low trust -> remains low Watch, not Critical!
        if flame and (temp > 45.0 or cam_conf > 0.4):
            # Confirmed active fire
            fused = 75.0 + (air_score * 0.15) + (temp_score * 0.10)
        else:
            fused = (
                air_score * 0.35 +
                temp_score * 0.30 +
                flame_score * 0.20 +
                cam_score * 0.15
            )

        factors = [
            {"factor": "Combustion Gas / Smoke", "weight": 0.35, "value": f"MQ-2: {mq2:.0f}, MQ-135: {mq135:.0f}", "score": round(air_score, 1)},
            {"factor": "Thermal Rise", "weight": 0.30, "value": f"{temp:.1f} °C", "score": round(temp_score, 1)},
            {"factor": "Optical Flame Sensor", "weight": 0.20, "value": "DETECTED" if flame else "CLEAR", "score": round(flame_score, 1)},
            {"factor": "Computer Vision Fire Stream", "weight": 0.15, "value": f"{cam_conf*100:.0f}%", "score": round(cam_score, 1)},
        ]

        return round(min(100.0, max(0.0, fused)), 1), factors

    def fuse_bhumi(
        self,
        metrics: Dict[str, Any],
        trust: Dict[str, float]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Fuse BHUMI Landslide Metrics:
        Soil saturation (upper + lower) + tilt displacement + vibration RMS + rain context.
        """
        m_up = float(metrics.get("soil_moisture_upper_pct", 30.0))
        m_low = float(metrics.get("soil_moisture_lower_pct", 35.0))
        tilt = float(metrics.get("tilt_delta_deg", 0.0))
        vib_rms = float(metrics.get("vibration_rms", 0.0))
        rain_ctx = float(metrics.get("rain_context", 0.0))

        u_trust = trust.get("soil_moisture_upper", 100.0) / 100.0
        tilt_trust = trust.get("inclinometer_tilt", 100.0) / 100.0
        vib_trust = trust.get("geophone_vibration", 100.0) / 100.0

        # Moisture saturation: > 75% critical
        sat_avg = (m_up * 0.6 + m_low * 0.4)
        sat_score = min(100.0, max(0.0, ((sat_avg - 30.0) / 50.0) * 100.0)) * u_trust

        # Tilt delta: > 5 degrees is severe slope failure
        tilt_score = min(100.0, max(0.0, (tilt / 5.0) * 100.0)) * tilt_trust

        # Vibration RMS: > 10 is continuous ground shear
        vib_score = min(100.0, max(0.0, (vib_rms / 10.0) * 100.0)) * vib_trust

        # Rain context
        rain_score = min(100.0, max(0.0, (rain_ctx / 60.0) * 100.0))

        # Correlated failure condition:
        # If soil is saturated (>70%) AND tilt delta is occurring (>2.5 deg), hazard is Critical!
        if sat_avg > 68.0 and tilt > 2.0:
            fused = 75.0 + (tilt_score * 0.15) + (vib_score * 0.10)
        else:
            fused = (
                sat_score * 0.35 +
                tilt_score * 0.35 +
                vib_score * 0.20 +
                rain_score * 0.10
            )

        factors = [
            {"factor": "Soil Pore Saturation", "weight": 0.35, "value": f"Upper {m_up:.0f}%, Lower {m_low:.0f}%", "score": round(sat_score, 1)},
            {"factor": "Slope Inclinometer Delta", "weight": 0.35, "value": f"{tilt:.2f}°", "score": round(tilt_score, 1)},
            {"factor": "Sub-surface Vibration RMS", "weight": 0.20, "value": f"{vib_rms:.2f} g", "score": round(vib_score, 1)},
            {"factor": "Precipitation Accumulation Context", "weight": 0.10, "value": f"{rain_ctx:.1f} mm", "score": round(rain_score, 1)},
        ]

        return round(min(100.0, max(0.0, fused)), 1), factors


sensor_fusion_engine = SensorFusionEngine()
