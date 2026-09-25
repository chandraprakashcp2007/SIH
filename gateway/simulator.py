"""
PRAHARI-NET Physical Environmental Telemetry Simulator
Generates realistic continuous physical transitions for:
- JALA-01 Flood hydrographs
- AGNI-02 Combustion kinetics & smoke plumes
- BHUMI-03 Geotechnical slope failure & shear slip
"""
import time
import random
import math
from typing import Dict, Any, Generator
from backend.app.core.config import settings


class PrahariSimulator:
    """Accurate physical process simulator for JALA, AGNI, and BHUMI."""

    def __init__(self):
        self.sequence_counters = {"JALA-01": 100, "AGNI-02": 100, "BHUMI-03": 100}
        self.active_scenario = "ALL_NORMAL"
        self.tick = 0
        self.internet_outage = False
        self.packet_loss_mode = False
        self.node_offline_id = None
        self.sensor_failure_metric = None

        # Base nominal states
        self.state = {
            "JALA-01": {
                "water_level_cm": 34.2,
                "water_distance_cm": 165.8,
                "water_rise_rate_cm_min": 0.0,
                "water_rise_acceleration": 0.0,
                "rain_intensity": 0.0,
                "temperature_c": 28.4,
                "humidity_pct": 74.0,
                "battery_pct": 94.0,
                "solar_voltage": 4.15,
                "signal_rssi": -76,
            },
            "AGNI-02": {
                "mq2_raw": 115.0,
                "mq135_raw": 128.0,
                "smoke_index": 4.2,
                "gas_index": 5.1,
                "temperature_c": 27.2,
                "humidity_pct": 68.0,
                "flame_detected": False,
                "camera_fire_confidence": 0.0,
                "camera_smoke_confidence": 0.0,
                "battery_pct": 91.0,
                "signal_rssi": -81,
            },
            "BHUMI-03": {
                "soil_moisture_upper_pct": 28.5,
                "soil_moisture_lower_pct": 33.0,
                "tilt_x_deg": 0.35,
                "tilt_y_deg": -0.22,
                "tilt_delta_deg": 0.12,
                "vibration_level": 0.8,
                "vibration_rms": 0.45,
                "rain_context": 5.0,
                "temperature_c": 24.5,
                "battery_pct": 88.0,
                "signal_rssi": -84,
            }
        }

    def set_scenario(self, scenario_name: str):
        """Set active simulation scenario and reset step tick."""
        self.active_scenario = scenario_name
        self.tick = 0
        if scenario_name == "ALL_NORMAL" or scenario_name == "RESET" or scenario_name == "RECOVERY":
            self.reset_to_nominal()
            self.active_scenario = "ALL_NORMAL"
        elif scenario_name == "INTERNET_OUTAGE":
            self.internet_outage = True
        elif scenario_name == "PACKET_LOSS":
            self.packet_loss_mode = True
        elif scenario_name == "NODE_OFFLINE":
            self.node_offline_id = "JALA-01"
        elif scenario_name == "SENSOR_FAILURE":
            self.sensor_failure_metric = "water_level_cm"

    def reset_to_nominal(self):
        self.internet_outage = False
        self.packet_loss_mode = False
        self.node_offline_id = None
        self.sensor_failure_metric = None
        self.state["JALA-01"]["water_level_cm"] = 34.2
        self.state["JALA-01"]["rain_intensity"] = 0.0
        self.state["JALA-01"]["water_rise_rate_cm_min"] = 0.0
        self.state["JALA-01"]["water_rise_acceleration"] = 0.0

        self.state["AGNI-02"]["mq2_raw"] = 115.0
        self.state["AGNI-02"]["mq135_raw"] = 128.0
        self.state["AGNI-02"]["temperature_c"] = 27.2
        self.state["AGNI-02"]["flame_detected"] = False
        self.state["AGNI-02"]["camera_fire_confidence"] = 0.0

        self.state["BHUMI-03"]["soil_moisture_upper_pct"] = 28.5
        self.state["BHUMI-03"]["soil_moisture_lower_pct"] = 33.0
        self.state["BHUMI-03"]["tilt_delta_deg"] = 0.12
        self.state["BHUMI-03"]["vibration_rms"] = 0.45
        self.state["BHUMI-03"]["rain_context"] = 5.0

    def step_simulation(self):
        """Advance physical simulation state by one cycle (~2 seconds)."""
        self.tick += 1
        t = self.tick

        # Add natural subtle analog sensor noise
        for nid in self.state:
            self.state[nid]["battery_pct"] = max(20.0, self.state[nid]["battery_pct"] - 0.001)

        # ----------------- JALA SCENARIOS -----------------
        if self.active_scenario == "FLOOD_RAMP":
            # Gradual rising water: Normal (34) -> Watch (75) -> Warning (135) -> Critical (195)
            # ~6 cm per tick
            self.state["JALA-01"]["rain_intensity"] = min(75.0, 15.0 + t * 4.0)
            rise_rate = min(5.5, 0.5 + t * 0.3)
            self.state["JALA-01"]["water_rise_rate_cm_min"] = rise_rate
            self.state["JALA-01"]["water_rise_acceleration"] = 0.12 if t < 15 else 0.02
            self.state["JALA-01"]["water_level_cm"] = min(220.0, 34.2 + (t * 7.5))

        elif self.active_scenario == "FLASH_FLOOD":
            # Violent sudden surge: water jumps 25 cm per tick with torrential rain
            self.state["JALA-01"]["rain_intensity"] = 115.0 + (random.random() * 10.0)
            self.state["JALA-01"]["water_rise_rate_cm_min"] = 14.5
            self.state["JALA-01"]["water_rise_acceleration"] = 0.85
            self.state["JALA-01"]["water_level_cm"] = min(260.0, 34.2 + (t * 22.0))

        # ----------------- AGNI SCENARIOS -----------------
        elif self.active_scenario == "FALSE_SMOKE_SENSOR_SPIKE":
            # Single MQ2 spikes violently to 850, but temperature remains 27°C, flame False, MQ135 baseline
            # This triggers Sensor Trust contradiction without causing false critical alarm!
            self.state["AGNI-02"]["mq2_raw"] = 820.0 + (random.random() * 40.0)
            self.state["AGNI-02"]["mq135_raw"] = 135.0  # Normal
            self.state["AGNI-02"]["temperature_c"] = 27.4  # Normal ambient
            self.state["AGNI-02"]["flame_detected"] = False
            self.state["AGNI-02"]["camera_fire_confidence"] = 0.0

        elif self.active_scenario == "FIRE_DEVELOPMENT":
            # Realistic wildfire development:
            # First 5 ticks: smoke rises (Watch)
            # Ticks 6-10: heat rises + MQ135 rises (Warning)
            # Ticks 11+: optical flame detected + camera confidence confirms (Critical)
            if t <= 5:
                self.state["AGNI-02"]["mq2_raw"] = min(450.0, 115.0 + t * 65.0)
                self.state["AGNI-02"]["mq135_raw"] = min(320.0, 128.0 + t * 35.0)
                self.state["AGNI-02"]["temperature_c"] = 28.0 + t * 0.8
                self.state["AGNI-02"]["flame_detected"] = False
                self.state["AGNI-02"]["camera_fire_confidence"] = 0.15
            elif t <= 10:
                self.state["AGNI-02"]["mq2_raw"] = min(780.0, 450.0 + (t - 5) * 60.0)
                self.state["AGNI-02"]["mq135_raw"] = min(580.0, 320.0 + (t - 5) * 50.0)
                self.state["AGNI-02"]["temperature_c"] = min(55.0, 32.0 + (t - 5) * 3.5)
                self.state["AGNI-02"]["flame_detected"] = False
                self.state["AGNI-02"]["camera_fire_confidence"] = 0.55
            else:
                self.state["AGNI-02"]["mq2_raw"] = 890.0
                self.state["AGNI-02"]["mq135_raw"] = 720.0
                self.state["AGNI-02"]["temperature_c"] = min(78.0, 55.0 + (t - 10) * 4.0)
                self.state["AGNI-02"]["flame_detected"] = True
                self.state["AGNI-02"]["camera_fire_confidence"] = 0.94

        elif self.active_scenario == "CONFIRMED_FIRE":
            self.state["AGNI-02"]["mq2_raw"] = 920.0
            self.state["AGNI-02"]["mq135_raw"] = 780.0
            self.state["AGNI-02"]["temperature_c"] = 72.5
            self.state["AGNI-02"]["flame_detected"] = True
            self.state["AGNI-02"]["camera_fire_confidence"] = 0.96

        # ----------------- BHUMI SCENARIOS -----------------
        elif self.active_scenario == "LANDSLIDE_SATURATION":
            # Rain accumulates, soil moisture reaches pore saturation limit (Watch -> Warning)
            self.state["BHUMI-03"]["rain_context"] = min(90.0, 10.0 + t * 8.0)
            self.state["BHUMI-03"]["soil_moisture_upper_pct"] = min(88.0, 30.0 + t * 5.5)
            self.state["BHUMI-03"]["soil_moisture_lower_pct"] = min(85.0, 35.0 + t * 4.5)
            self.state["BHUMI-03"]["tilt_delta_deg"] = min(1.2, 0.12 + t * 0.09)
            self.state["BHUMI-03"]["vibration_rms"] = 1.2

        elif self.active_scenario == "LANDSLIDE_MOVEMENT":
            # Fully saturated slope shears and tilts (Critical!)
            self.state["BHUMI-03"]["rain_context"] = 110.0
            self.state["BHUMI-03"]["soil_moisture_upper_pct"] = 92.0
            self.state["BHUMI-03"]["soil_moisture_lower_pct"] = 94.0
            self.state["BHUMI-03"]["tilt_delta_deg"] = min(7.5, 1.2 + t * 0.7)
            self.state["BHUMI-03"]["vibration_rms"] = min(18.5, 2.0 + t * 1.8)

        elif self.active_scenario == "SENSOR_FAILURE":
            # In sensor failure, a sensor gets frozen or outputs NaN/jump
            self.state["JALA-01"]["water_level_cm"] = 999.9  # Out of bounds jump!

    def generate_packets(self) -> Dict[str, Dict[str, Any]]:
        """Produce 3 LoRa JSON packets adhering to protocol.json."""
        packets = {}
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+05:30", time.localtime())

        for node_id, metrics in self.state.items():
            if self.node_offline_id == node_id:
                continue  # Simulate dropped/offline node

            self.sequence_counters[node_id] += 1
            seq = self.sequence_counters[node_id]

            if self.packet_loss_mode and random.random() < 0.35:
                # Simulate packet loss gap
                self.sequence_counters[node_id] += 1
                continue

            rssi = metrics.get("signal_rssi", -78) + random.randint(-2, 2)
            battery = round(metrics.get("battery_pct", 95.0), 1)

            # Node-specific clean metric copy
            node_metrics = {}
            for k, v in metrics.items():
                if k not in ["battery_pct", "signal_rssi"]:
                    if not settings.VISION_ENABLED and k in {
                        "camera_fire_confidence", "camera_smoke_confidence"
                    }:
                        continue
                    if isinstance(v, float):
                        value = v + (random.uniform(-0.15, 0.15) if "raw" not in k else 0)
                        if k in {"rain_intensity", "rain_context", "water_level_cm", "water_distance_cm", "vibration_level", "vibration_rms"}:
                            value = max(0.0, value)
                        if k in {"humidity_pct", "soil_moisture_upper_pct", "soil_moisture_lower_pct"}:
                            value = min(100.0, max(0.0, value))
                        node_metrics[k] = round(value, 2)
                    else:
                        node_metrics[k] = v

            packet = {
                "version": 1,
                "node_id": node_id,
                "sequence": seq,
                "timestamp": now_iso,
                "metrics": node_metrics,
                "rssi": rssi,
                "battery_pct": battery,
                "is_simulation": True,
                "source_mode": "SIMULATION",
                "transport": "SIMULATOR"
            }
            packets[node_id] = packet

        return packets


prahari_sim = PrahariSimulator()
