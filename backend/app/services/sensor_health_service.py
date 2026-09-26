from datetime import datetime

from backend.app.models.nodes import Node
from backend.app.models.observations import Observation
from backend.app.models.sensor_health import SensorHealthSnapshot


def health_snapshots(
    *, node: Node, observations: list[Observation], trust_scores: dict[str, float],
    battery_pct: float, rssi: int, provenance: str, recorded_at: datetime,
) -> list[SensorHealthSnapshot]:
    trust_values = list(trust_scores.values())
    trust = round(sum(trust_values) / len(trust_values), 2) if trust_values else 50.0
    reasons: list[str] = []
    if trust < 40:
        state = "SUSPECT"
        reasons.append("LOW_TRUST")
    elif trust < 70:
        state = "DEGRADED"
        reasons.append("REDUCED_TRUST")
    else:
        state = "HEALTHY"
    if battery_pct < 20:
        state = "DEGRADED" if state == "HEALTHY" else state
        reasons.append("LOW_BATTERY")
    if rssi < -110:
        state = "DEGRADED" if state == "HEALTHY" else state
        reasons.append("WEAK_SIGNAL")
    return [SensorHealthSnapshot(
        node_id=node.id, sensor_id=item.sensor_id, state=state,
        trust_score=trust, noise_score=None, drift_score=None,
        missing_data_pct=0, battery_pct=battery_pct, rssi=rssi,
        calibration_state="NOT_CONFIGURED", firmware_version=node.firmware_version,
        provenance=provenance, reason_codes=reasons, recorded_at=recorded_at,
    ) for item in observations]
