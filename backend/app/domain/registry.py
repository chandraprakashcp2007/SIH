from dataclasses import asdict, dataclass
from typing import Any

from backend.app.provenance import SourceMode


@dataclass(frozen=True)
class HardwareProfile:
    controller: str
    sensors: tuple[str, ...]
    transport: dict[str, str]
    power: str
    enclosure: str
    firmware_version: str
    source_mode: SourceMode
    capabilities: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_mode"] = self.source_mode.value
        return data


@dataclass(frozen=True)
class DomainDefinition:
    domain_id: str
    display_name: str
    element: str
    primary_hazards: tuple[str, ...]
    supported_metrics: tuple[str, ...]
    default_source_mode: SourceMode
    hardware_state: str
    risk_engine_available: bool
    description: str
    hardware_profile: HardwareProfile


def _profile(controller: str, sensors: tuple[str, ...], source: SourceMode, live_serial: bool = False) -> HardwareProfile:
    return HardwareProfile(
        controller=controller,
        sensors=sensors,
        transport={
            "USB_SERIAL": "LIVE" if live_serial else "SUPPORTED",
            "WIFI": "SUPPORTED",
            "LORA": "PLANNED",
            "LORAWAN": "PLANNED",
            "NB_IOT": "PLANNED",
            "CELLULAR": "PLANNED",
            "5G": "PLANNED",
        },
        power="USB_BENCH" if live_serial else "PLANNED",
        enclosure="BENCH_PROTOTYPE" if live_serial else "PLANNED",
        firmware_version="ESP8266_PROTOTYPE" if live_serial else "PLANNED",
        source_mode=source,
        capabilities=("sensor_acquisition", "sanity_checks", "local_threshold_alert"),
    )


DOMAIN_REGISTRY: dict[str, DomainDefinition] = {
    "JALA-01": DomainDefinition("JALA-01", "JALA", "WATER", ("FLOOD", "FLASH_FLOOD"), ("water_level_cm", "rain_intensity", "temperature_c", "humidity_pct"), SourceMode.SIMULATION, "ESP8266_PROTOTYPE_AVAILABLE", True, "Water-level and flood intelligence.", _profile("ESP8266", ("water_level", "rainfall", "temperature_humidity"), SourceMode.SIMULATION, True)),
    "AGNI-02": DomainDefinition("AGNI-02", "AGNI", "FIRE", ("FOREST_FIRE", "SMOKE"), ("mq2_raw", "mq135_raw", "temperature_c", "flame_detected"), SourceMode.SIMULATION, "PLANNED_FIELD_NODE", True, "Fire, smoke and combustion intelligence.", _profile("ESP32", ("smoke_gas", "temperature", "flame"), SourceMode.SIMULATION)),
    "BHUMI-03": DomainDefinition("BHUMI-03", "BHUMI", "EARTH", ("LANDSLIDE", "SLOPE_INSTABILITY"), ("soil_moisture_upper_pct", "tilt_delta_deg", "vibration_rms", "rain_context"), SourceMode.SIMULATION, "PLANNED_FIELD_NODE", True, "Soil saturation and slope stability intelligence.", _profile("ESP32", ("soil_moisture", "tilt", "vibration"), SourceMode.SIMULATION)),
    "VAYU-04": DomainDefinition("VAYU-04", "VAYU", "AIR", ("AIR_POLLUTION", "HAZARDOUS_GAS"), ("pm2_5", "pm10", "co_ppm", "voc_index"), SourceMode.SIMULATION, "SOFTWARE_ACTIVE_HW_NOT_CONNECTED", True, "Air-quality intelligence software is active; physical sensors remain explicitly disconnected until connected.", _profile("ESP32", ("particulate", "gas", "environmental"), SourceMode.SIMULATION)),
    "AKASHA-05": DomainDefinition("AKASHA-05", "AKASHA", "ATMOSPHERE", ("EXTREME_WEATHER", "CYCLONE_CONTEXT"), ("rain_intensity", "pressure_hpa", "wind_speed_kmh", "wind_gust_kmh"), SourceMode.SIMULATION, "SOFTWARE_ACTIVE_HW_NOT_CONNECTED", True, "Atmospheric intelligence software is active; physical weather sensors and external feeds retain explicit provenance.", _profile("ESP32", ("pressure", "rainfall", "wind"), SourceMode.SIMULATION)),
}


GATEWAY_PROFILE = HardwareProfile(
    controller="WINDOWS_PYTHON_GATEWAY",
    sensors=(),
    transport={"USB_SERIAL": "LIVE", "WIFI": "SUPPORTED", "LORA": "PLANNED", "LORAWAN": "PLANNED"},
    power="MAINS",
    enclosure="DEVELOPMENT_LAPTOP",
    firmware_version="PYTHON_GATEWAY",
    source_mode=SourceMode.REAL,
    capabilities=("fastapi", "database", "evidence_fusion", "store_forward_foundation"),
)
