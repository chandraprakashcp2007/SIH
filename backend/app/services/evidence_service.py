from typing import Any, Dict


def build_event_evidence(**fields: Any) -> Dict[str, Any]:
    """Create the stable evidence envelope stored with every incident."""
    required = (
        "event_id", "node_id", "hazard", "timestamp", "raw_telemetry",
        "processed_features", "risk", "confidence", "sensor_trust",
        "explanation", "gateway_state", "network_state", "processing_latency_ms",
    )
    return {key: fields.get(key) for key in required}
