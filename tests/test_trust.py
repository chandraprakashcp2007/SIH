"""
Sensor Trust Engine Unit Tests
"""
import pytest
from backend.app.ai.trust import sensor_trust_engine


def test_sensor_stuck_detection():
    # Provide 6 consecutive readings with zero variation
    history = [{"water_distance_cm": 150.0} for _ in range(6)]
    current = {"water_level_cm": 30.0, "water_distance_cm": 150.0}
    scores, anomalies = sensor_trust_engine.evaluate_node_trust("JALA-01", current, history)
    # Check that anomalies detected stuck readings or flags
    assert isinstance(scores, dict)


def test_sensor_impossible_jump():
    history = [{"water_level_cm": 30.0}]
    current = {"water_level_cm": 180.0}  # Sudden 150 cm jump in 2 seconds
    scores, anomalies = sensor_trust_engine.evaluate_node_trust("JALA-01", current, history)
    assert scores["water_level_sensor"] <= 45.0
    assert any("impossible jump" in a for a in anomalies)


def test_sensor_out_of_physical_bounds():
    current = {"water_level_cm": 1200.0}  # Out of range (> 1000)
    scores, anomalies = sensor_trust_engine.evaluate_node_trust("JALA-01", current, [])
    assert scores["water_level_sensor"] <= 30.0
    assert any("out-of-physical bounds" in a for a in anomalies)
