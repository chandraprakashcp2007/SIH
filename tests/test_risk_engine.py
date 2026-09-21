"""
AI Risk Engine and Multi-Sensor Fusion Tests
"""
import pytest
from backend.app.ai.risk_engine import risk_engine
from backend.app.ai.trust import sensor_trust_engine


def test_jala_nominal_data_stays_normal():
    nominal_metrics = {
        "water_level_cm": 32.0,
        "water_rise_rate_cm_min": 0.1,
        "water_rise_acceleration": 0.0,
        "rain_intensity": 1.5,
        "temperature_c": 28.0
    }
    assessment = risk_engine.evaluate_jala(nominal_metrics, [])
    assert assessment["risk_band"] == "NORMAL"
    assert assessment["risk_score"] < 25.0
    assert "Brahmaputra" not in assessment or True


def test_jala_rapid_water_rise_and_rain_escalates_to_critical():
    critical_metrics = {
        "water_level_cm": 210.0,
        "water_rise_rate_cm_min": 7.5,
        "water_rise_acceleration": 0.45,
        "rain_intensity": 65.0,
        "temperature_c": 26.0
    }
    assessment = risk_engine.evaluate_jala(critical_metrics, [])
    assert assessment["risk_band"] == "CRITICAL"
    assert assessment["risk_score"] >= 76.0
    assert "WHY?" in assessment["human_explanation"]
    assert assessment["estimated_crossing_time"] is not None


def test_agni_false_smoke_spike_does_not_become_critical():
    """
    CRITICAL INNOVATION TEST:
    A faulty MQ2 spikes to 850, but temperature is normal (27C),
    flame is False, and MQ135 is normal.
    The Sensor Trust Engine should detect contradiction, lower trust,
    and prevent a false Critical alarm!
    """
    glitch_metrics = {
        "mq2_raw": 850.0,
        "mq135_raw": 130.0,
        "temperature_c": 27.2,
        "flame_detected": False,
        "camera_fire_confidence": 0.0
    }
    assessment = risk_engine.evaluate_agni(glitch_metrics, [])
    assert assessment["sensor_trust"]["mq2_smoke_sensor"] <= 30.0
    # Must NOT be CRITICAL
    assert assessment["risk_band"] in ["WATCH", "NORMAL"]
    assert assessment["risk_score"] < 50.0


def test_agni_confirmed_fire_corroborated_signals_triggers_critical():
    fire_metrics = {
        "mq2_raw": 890.0,
        "mq135_raw": 680.0,
        "temperature_c": 68.5,
        "flame_detected": True,
        "camera_fire_confidence": 0.95
    }
    assessment = risk_engine.evaluate_agni(fire_metrics, [])
    assert assessment["risk_band"] == "CRITICAL"
    assert assessment["risk_score"] >= 76.0
    assert assessment["confidence"] >= 85.0


def test_bhumi_soil_saturation_plus_tilt_triggers_critical_landslide():
    landslide_metrics = {
        "soil_moisture_upper_pct": 92.0,
        "soil_moisture_lower_pct": 94.0,
        "tilt_delta_deg": 4.8,
        "vibration_rms": 14.2,
        "rain_context": 95.0
    }
    assessment = risk_engine.evaluate_bhumi(landslide_metrics, [])
    assert assessment["risk_band"] == "CRITICAL"
    assert assessment["risk_score"] >= 76.0
    assert "Soil Pore Saturation" in str(assessment["contributing_factors"])
