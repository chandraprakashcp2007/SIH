import random

import pytest
from sqlalchemy import func, select

from backend.app.core.config import settings
from backend.app.core.database import AsyncSessionLocal
from backend.app.copilot.intent import extract_node_entity
from backend.app.copilot.retrieval import LocalKnowledgeRetriever
from backend.app.copilot.response_generator import ResponseGenerator
from backend.app.copilot.fallback import deterministic_fallback
from backend.app.copilot.intent import IntentMatch, INTENT_NODE_STATUS
from backend.app.copilot.schemas import ToolResult
from backend.app.models.alerts import Alert
from backend.app.models.risk import RiskAssessment
from backend.app.models.telemetry import TelemetryRecord
from backend.app.services.telemetry_service import telemetry_service
from gateway.simulator import PrahariSimulator


def test_explicit_unknown_node_id_is_not_rewritten_to_known_alias():
    assert extract_node_entity("what is the status of node JALA-99?") == "JALA-99"


def test_unknown_node_response_is_explicit_and_never_fabricates_normal_state():
    answer, components = ResponseGenerator.format_node_status(
        {"error": "Node JALA-99 not found in database."},
        {"error": "No telemetry records available for node JALA-99."},
        {"error": "No risk assessment found for JALA-99."},
    )
    assert answer == "Node JALA-99 not found in database."
    assert components == []


def test_failed_unknown_node_tool_never_formats_a_nominal_card():
    answer, components = deterministic_fallback.format_fallback_response(
        IntentMatch(intent=INTENT_NODE_STATUS, confidence=1.0, entities={"node_id": "JALA-99"}, fast_path_eligible=True),
        [ToolResult(success=False, tool="get_node_status", error="Node JALA-99 not found in database.")],
    )
    assert answer == "Node JALA-99 not found in database."
    assert components == []


def test_retrieval_prefers_dedicated_jala_document():
    retriever = LocalKnowledgeRetriever()
    retriever.build_index(force=True)
    result = retriever.retrieve("How does JALA measure water level?", top_k=1)
    assert result[0]["document"] == "docs/jala.md"


def test_simulator_never_emits_negative_environmental_values(monkeypatch):
    monkeypatch.setattr(settings, "VISION_ENABLED", False)
    random.seed(7)
    simulator = PrahariSimulator()

    for _ in range(100):
        simulator.step_simulation()
        packets = simulator.generate_packets()
        assert packets["JALA-01"]["metrics"]["rain_intensity"] >= 0
        assert 0 <= packets["JALA-01"]["metrics"]["humidity_pct"] <= 100
        assert 0 <= packets["BHUMI-03"]["metrics"]["rain_context"]


def test_simulator_omits_camera_evidence_when_vision_is_disabled(monkeypatch):
    monkeypatch.setattr(settings, "VISION_ENABLED", False)
    simulator = PrahariSimulator()
    simulator.set_scenario("CONFIRMED_FIRE")
    simulator.step_simulation()

    metrics = simulator.generate_packets()["AGNI-02"]["metrics"]

    assert "camera_fire_confidence" not in metrics
    assert "camera_smoke_confidence" not in metrics


@pytest.mark.asyncio
async def test_duplicate_packet_has_no_persistence_or_alert_side_effects():
    telemetry_service.reset_sequence_tracking()
    payload = {
        "version": 1,
        "node_id": "JALA-01",
        "sequence": 987654,
        "metrics": {
            "water_level_cm": 220.0,
            "water_distance_cm": 0.0,
            "water_rise_rate_cm_min": 15.0,
            "water_rise_acceleration": 1.0,
            "rain_intensity": 120.0,
            "temperature_c": 28.0,
            "humidity_pct": 80.0,
        },
        "rssi": -70,
        "battery_pct": 90.0,
        "is_simulation": True,
    }

    async with AsyncSessionLocal() as db:
        first = await telemetry_service.ingest_packet(db, payload, "TEST")
        before = {
            "telemetry": await db.scalar(select(func.count()).select_from(TelemetryRecord)),
            "risk": await db.scalar(select(func.count()).select_from(RiskAssessment)),
            "alerts": await db.scalar(select(func.count()).select_from(Alert)),
        }
        duplicate = await telemetry_service.ingest_packet(db, payload, "TEST")
        after = {
            "telemetry": await db.scalar(select(func.count()).select_from(TelemetryRecord)),
            "risk": await db.scalar(select(func.count()).select_from(RiskAssessment)),
            "alerts": await db.scalar(select(func.count()).select_from(Alert)),
        }

    assert first["status"] == "success"
    assert duplicate["status"] == "duplicate"
    assert after == before
