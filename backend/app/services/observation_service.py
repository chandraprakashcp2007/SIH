"""Adapters from legacy packet telemetry to canonical observations."""
import hashlib
import json
from datetime import datetime
from typing import Any

from backend.app.domain.registry import DOMAIN_REGISTRY
from backend.app.models.nodes import Node
from backend.app.models.observations import Observation
from backend.app.provenance import SourceMode


METRIC_UNITS = {
    "water_level_cm": "cm",
    "water_distance_cm": "cm",
    "water_rise_rate_cm_min": "cm/min",
    "water_rise_acceleration": "cm/min^2",
    "rain_intensity": "mm/h",
    "rain_context": "mm/h",
    "temperature_c": "Cel",
    "humidity_pct": "%",
    "soil_moisture_upper_pct": "%",
    "soil_moisture_lower_pct": "%",
    "tilt_x_deg": "deg",
    "tilt_y_deg": "deg",
    "tilt_delta_deg": "deg",
    "vibration_level": "1",
    "vibration_rms": "1",
    "pressure_hpa": "hPa",
    "pressure_drop_hpa_3h": "hPa/3h",
    "wind_speed_kmh": "km/h",
    "wind_gust_kmh": "km/h",
    "pm2_5": "ug/m3",
    "pm10": "ug/m3",
    "co_ppm": "ppm",
    "mq2_raw": "1",
    "mq135_raw": "1",
    "smoke_index": "1",
    "gas_index": "1",
    "voc_index": "1",
    "flame_detected": "1",
}


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def adapt_legacy_metrics(
    *,
    node: Node,
    metrics: dict[str, Any],
    payload: dict[str, Any],
    sequence_number: int,
    timestamp: datetime,
    received_at: datetime,
    source: str,
    provenance: SourceMode,
    trust_scores: dict[str, float] | None = None,
) -> list[Observation]:
    definition = DOMAIN_REGISTRY[node.id]
    trust_values = list((trust_scores or {}).values())
    trust = sum(trust_values) / len(trust_values) if trust_values else 50.0
    freshness = max(0.0, (received_at - timestamp).total_seconds())
    payload_hash = canonical_payload_hash(payload)
    observations = []
    for property_name, value in metrics.items():
        if not isinstance(value, (bool, int, float)):
            continue
        observations.append(Observation(
            node_id=node.id,
            sensor_id=f"{node.id}:{property_name}",
            domain=definition.display_name,
            observed_property=property_name,
            value=value,
            unit=METRIC_UNITS.get(property_name),
            timestamp=timestamp,
            received_at=received_at,
            latitude=node.latitude,
            longitude=node.longitude,
            source=source,
            provenance=provenance.value,
            quality_score=1.0,
            trust_score=round(trust, 2),
            freshness_seconds=round(freshness, 3),
            sequence_number=sequence_number,
            firmware_version=node.firmware_version,
            metadata_info={"legacy_adapter": "telemetry.v1"},
            raw_payload_hash=payload_hash,
        ))
    return observations
