from datetime import datetime, timedelta, timezone

from backend.app.services.readiness_service import derive_gateway_state
from backend.app.services.evidence_service import build_event_evidence


def test_gateway_state_is_offline_when_no_packets_exist():
    status = derive_gateway_state(None, datetime.now(timezone.utc), timeout_seconds=10)
    assert status["status"] == "OFFLINE"
    assert status["last_packet_age_seconds"] is None


def test_gateway_state_uses_last_packet_freshness():
    now = datetime.now(timezone.utc)
    fresh = derive_gateway_state(now - timedelta(seconds=3), now, timeout_seconds=10)
    stale = derive_gateway_state(now - timedelta(seconds=30), now, timeout_seconds=10)
    assert fresh["status"] == "CONNECTED"
    assert stale["status"] == "STALE"


def test_event_evidence_contains_required_operational_context():
    evidence = build_event_evidence(
        event_id="EVT-1",
        node_id="JALA-01",
        hazard="FLOOD",
        timestamp="2026-09-21T00:00:00Z",
        raw_telemetry={"water_level_cm": 190},
        processed_features={"rise_rate": 6.8},
        risk={"score": 91, "band": "CRITICAL"},
        confidence=97,
        sensor_trust={"water": 97},
        explanation="Rapid rise",
        gateway_state={"status": "CONNECTED"},
        network_state={"packet_loss_pct": 0},
        processing_latency_ms=12.5,
    )
    assert set(evidence) >= {
        "event_id", "node_id", "hazard", "timestamp", "raw_telemetry",
        "processed_features", "risk", "confidence", "sensor_trust",
        "explanation", "gateway_state", "network_state", "processing_latency_ms",
    }
