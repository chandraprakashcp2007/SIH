"""
Tests for Copilot Intent Classification & Memory Pronoun Resolution
"""
import pytest
from backend.app.copilot.intent import (
    classify_intent,
    INTENT_LIVE_STATUS,
    INTENT_NODE_STATUS,
    INTENT_TELEMETRY_QUERY,
    INTENT_ALERT_QUERY,
    INTENT_EVENT_QUERY,
    INTENT_NETWORK_QUERY,
    INTENT_DEVICE_HEALTH,
    INTENT_PREDICTION_QUERY,
    INTENT_DOCUMENTATION_QUERY,
    INTENT_COMPARISON
)
from backend.app.copilot.memory import conversation_memory


def test_highest_risk_intent():
    match = classify_intent("Which node currently has the highest risk?")
    assert match.intent == INTENT_LIVE_STATUS
    assert match.entities.get("query_type") == "HIGHEST_RISK"
    assert match.fast_path_eligible is True


def test_why_jala_intent():
    match = classify_intent("Why is JALA in warning state?")
    assert match.intent == INTENT_NODE_STATUS
    assert match.entities.get("node_id") == "JALA-01"
    assert match.fast_path_eligible is True


def test_why_agni_intent():
    match = classify_intent("Explain why AGNI-02 triggered a fire alert.")
    assert match.intent == INTENT_NODE_STATUS
    assert match.entities.get("node_id") == "AGNI-02"


def test_why_bhumi_intent():
    match = classify_intent("Why is BHUMI critical?")
    assert match.intent == INTENT_NODE_STATUS
    assert match.entities.get("node_id") == "BHUMI-03"


@pytest.mark.parametrize(
    ("query", "intent", "node_id"),
    [
        ("VAYU status", INTENT_NODE_STATUS, "VAYU-04"),
        ("AKASHA telemetry", INTENT_TELEMETRY_QUERY, "AKASHA-05"),
        ("Show vayu-04 readings", INTENT_TELEMETRY_QUERY, "VAYU-04"),
        ("Why is akasha-05 in warning?", INTENT_NODE_STATUS, "AKASHA-05"),
    ],
)
def test_vayu_and_akasha_direct_queries_route_to_node_tools(query, intent, node_id):
    match = classify_intent(query)
    assert match.intent == intent
    assert match.entities.get("node_id") == node_id


def test_weakest_rssi_intent():
    match = classify_intent("Which node has the weakest LoRa signal?")
    assert match.intent == INTENT_NETWORK_QUERY
    assert match.entities.get("query_type") == "WEAKEST_RSSI"


def test_low_trust_intent():
    match = classify_intent("Which sensor currently has low trust?")
    assert match.intent == INTENT_DEVICE_HEALTH
    assert match.entities.get("query_type") == "LOW_TRUST"


def test_gateway_connectivity_intent():
    match = classify_intent("Is the gateway connected?")
    assert match.intent == INTENT_NETWORK_QUERY
    assert match.entities.get("query_type") == "GATEWAY_STATUS"


def test_active_and_unack_alerts_intent():
    match1 = classify_intent("Show unacknowledged alerts.")
    assert match1.intent == INTENT_ALERT_QUERY
    assert match1.entities.get("query_type") == "UNACKNOWLEDGED"

    match2 = classify_intent("What are the active alerts?")
    assert match2.intent == INTENT_ALERT_QUERY
    assert match2.entities.get("query_type") == "ACTIVE"


def test_comparison_intent():
    match = classify_intent("Compare JALA and BHUMI risk.")
    assert match.intent == INTENT_COMPARISON
    assert "JALA-01" in match.entities.get("nodes", [])
    assert "BHUMI-03" in match.entities.get("nodes", [])


def test_telemetry_trend_intent():
    match = classify_intent("Show the last 10 minutes of JALA water trend.")
    assert match.intent == INTENT_TELEMETRY_QUERY
    assert match.entities.get("node_id") == "JALA-01"
    assert match.entities.get("window_minutes") == 10


def test_documentation_intent():
    match = classify_intent("How does PRAHARI reduce false alarms?")
    assert match.intent == INTENT_DOCUMENTATION_QUERY


def test_pronoun_resolution():
    sess_id = "test-session-memory-1"
    conversation_memory.get_or_create(sess_id).update(node_id="JALA-01")

    resolved, last_node = conversation_memory.resolve_pronouns("Why is it critical?", sess_id)
    assert "JALA-01" in resolved
    assert last_node == "JALA-01"


def test_basic_tanglish_operational_intents():
    assert classify_intent("gateway okay ah").intent == INTENT_NETWORK_QUERY
    alerts = classify_intent("alert ethavathu iruka")
    assert alerts.intent == INTENT_ALERT_QUERY
    assert alerts.entities["query_type"] == "ACTIVE"
