"""
PRAHARI Copilot Intent Classification Engine
Fast deterministic intent router categorizing operational queries in sub-millisecond time.
"""
import re
from typing import Dict, Any, Optional, Tuple, List

# Intent Constants
INTENT_LIVE_STATUS = "LIVE_STATUS"
INTENT_NODE_STATUS = "NODE_STATUS"
INTENT_TELEMETRY_QUERY = "TELEMETRY_QUERY"
INTENT_ALERT_QUERY = "ALERT_QUERY"
INTENT_EVENT_QUERY = "EVENT_QUERY"
INTENT_NETWORK_QUERY = "NETWORK_QUERY"
INTENT_DEVICE_HEALTH = "DEVICE_HEALTH"
INTENT_PREDICTION_QUERY = "PREDICTION_QUERY"
INTENT_ANALYTICS_QUERY = "ANALYTICS_QUERY"
INTENT_DOCUMENTATION_QUERY = "DOCUMENTATION_QUERY"
INTENT_SYSTEM_EXPLANATION = "SYSTEM_EXPLANATION"
INTENT_COMPARISON = "COMPARISON"
INTENT_UNKNOWN = "UNKNOWN"

# Node synonyms mapping
NODE_MAP = {
    "jala": "JALA-01",
    "jala-01": "JALA-01",
    "flood": "JALA-01",
    "water": "JALA-01",
    "river": "JALA-01",
    "agni": "AGNI-02",
    "agni-02": "AGNI-02",
    "fire": "AGNI-02",
    "smoke": "AGNI-02",
    "combustion": "AGNI-02",
    "bhumi": "BHUMI-03",
    "bhumi-03": "BHUMI-03",
    "landslide": "BHUMI-03",
    "tilt": "BHUMI-03",
    "slope": "BHUMI-03",
    "inclinometer": "BHUMI-03",
    "vayu": "VAYU-04",
    "vayu-04": "VAYU-04",
    "air quality": "VAYU-04",
    "akasha": "AKASHA-05",
    "akasha-05": "AKASHA-05",
    "atmosphere": "AKASHA-05",
    "weather": "AKASHA-05",
}


class IntentMatch:
    def __init__(
        self,
        intent: str,
        confidence: float,
        fast_path_eligible: bool,
        entities: Dict[str, Any]
    ):
        self.intent = intent
        self.confidence = confidence
        self.fast_path_eligible = fast_path_eligible
        self.entities = entities

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "fast_path_eligible": self.fast_path_eligible,
            "entities": self.entities
        }


def extract_node_entity(q: str) -> Optional[str]:
    """Extract node ID from query text."""
    explicit_id = re.search(r'\b(jala|agni|bhumi|vayu|akasha)-\d+\b', q, re.IGNORECASE)
    if explicit_id:
        return explicit_id.group(0).upper()
    for key, val in NODE_MAP.items():
        # Match whole word
        if re.search(rf'\b{re.escape(key)}\b', q):
            return val
    return None


def extract_time_window(q: str) -> int:
    """Extract temporal window in minutes, default 10."""
    m = re.search(r'(\d+)\s*(?:minute|min)', q)
    if m:
        return int(m.group(1))
    if "hour" in q:
        return 60
    return 10


def classify_intent(query: str, session_node: Optional[str] = None) -> IntentMatch:
    """
    Sub-millisecond deterministic intent router.
    Evaluates pattern matching across operational keywords.
    """
    q = query.lower().strip()
    node_id = extract_node_entity(q) or session_node
    time_window = extract_time_window(q)

    # 1. COMPARISON
    if ("compare" in q or "versus" in q or " vs " in q or "difference between" in q) and ("risk" in q or "node" in q or "health" in q or "rssi" in q or "battery" in q):
        nodes_found = []
        for n_key, n_val in [
            ("jala", "JALA-01"),
            ("agni", "AGNI-02"),
            ("bhumi", "BHUMI-03"),
            ("vayu", "VAYU-04"),
            ("akasha", "AKASHA-05"),
        ]:
            if n_key in q:
                nodes_found.append(n_val)
        return IntentMatch(
            intent=INTENT_COMPARISON,
            confidence=0.98,
            fast_path_eligible=True,
            entities={"nodes": nodes_found or ["JALA-01", "BHUMI-03"], "aspect": "risk"}
        )

    # 2. HIGHEST RISK / WORST HAZARD
    if "highest risk" in q or "worst risk" in q or "most dangerous" in q or "maximum risk" in q or "top risk" in q:
        return IntentMatch(
            intent=INTENT_LIVE_STATUS,
            confidence=0.99,
            fast_path_eligible=True,
            entities={"query_type": "HIGHEST_RISK"}
        )

    # 3. WEAKEST RSSI / WEAKEST SIGNAL
    if "weakest" in q and ("rssi" in q or "signal" in q or "link" in q or "rf" in q):
        return IntentMatch(
            intent=INTENT_NETWORK_QUERY,
            confidence=0.99,
            fast_path_eligible=True,
            entities={"query_type": "WEAKEST_RSSI"}
        )

    # 4. LOW TRUST SENSORS / SENSOR FAILURE
    if ("trust" in q or "sensor failure" in q or "faulty sensor" in q or "unreliable sensor" in q) and "explain" not in q:
        return IntentMatch(
            intent=INTENT_DEVICE_HEALTH,
            confidence=0.99,
            fast_path_eligible=True,
            entities={"query_type": "LOW_TRUST"}
        )

    # 5. GATEWAY STATUS / OFFLINE CONNECTIVITY
    if ("gateway" in q and ("connected" in q or "status" in q or "health" in q or "okay" in q)) or ("running offline" in q or "internet outage" in q or "local edge" in q):
        return IntentMatch(
            intent=INTENT_NETWORK_QUERY,
            confidence=0.99,
            fast_path_eligible=True,
            entities={"query_type": "GATEWAY_STATUS"}
        )

    # 6. UNACKNOWLEDGED / ACTIVE ALERTS
    tanglish_alert = "alert" in q and any(term in q for term in ("ethavathu", "iruka", "irukaa", "irukka", "edhavadhu"))
    if "unacknowledged" in q or "active alert" in q or "active alarm" in q or "pending alert" in q or tanglish_alert or (q.startswith("alerts") or q == "show alerts"):
        return IntentMatch(
            intent=INTENT_ALERT_QUERY,
            confidence=0.99,
            fast_path_eligible=True,
            entities={"query_type": "UNACKNOWLEDGED" if "unack" in q else "ACTIVE"}
        )

    # 7. SPECIFIC NODE WHY / STATUS
    if node_id and ("why" in q or "critical" in q or "warning" in q or "status" in q or "condition" in q):
        return IntentMatch(
            intent=INTENT_NODE_STATUS,
            confidence=0.95,
            fast_path_eligible=True,
            entities={"node_id": node_id}
        )

    # 8. TELEMETRY / SENSOR TREND (e.g. "Show JALA water trend for last 10 minutes")
    if node_id and ("trend" in q or "level" in q or "reading" in q or "telemetry" in q or "chart" in q or "history" in q):
        return IntentMatch(
            intent=INTENT_TELEMETRY_QUERY,
            confidence=0.95,
            fast_path_eligible=True,
            entities={"node_id": node_id, "window_minutes": time_window}
        )

    # 9. EVENT / INCIDENT EVIDENCE (e.g. "What happened during EVT-001?" or "Why did alert trigger?")
    evt_match = re.search(r'\b(evt-\d+|alt-[a-zA-Z0-9]+)\b', q)
    if evt_match or "why did this alert" in q or "explain alert" in q or "latest alert" in q or "latest event" in q:
        event_id = evt_match.group(1).upper() if evt_match else None
        return IntentMatch(
            intent=INTENT_EVENT_QUERY,
            confidence=0.95,
            fast_path_eligible=True,
            entities={"event_id": event_id}
        )

    # 10. PREDICTIONS & THRESHOLD CROSSING
    if "predict" in q or "crossing" in q or "forecast" in q or "projection" in q or "next 5" in q or "future" in q:
        return IntentMatch(
            intent=INTENT_PREDICTION_QUERY,
            confidence=0.92,
            fast_path_eligible=True,
            entities={"node_id": node_id}
        )

    # 11. FLEET HEALTH / MAINTENANCE
    if "maintenance" in q or "device health" in q or "battery" in q or "devices need" in q:
        return IntentMatch(
            intent=INTENT_DEVICE_HEALTH,
            confidence=0.92,
            fast_path_eligible=True,
            entities={"query_type": "MAINTENANCE"}
        )

    # 12. GENERAL SYSTEM SUMMARY (e.g. "How is the system?", "Show system health", "status")
    if "how is the system" in q or "system health" in q or "fleet status" in q or "system status" in q or q == "status":
        return IntentMatch(
            intent=INTENT_LIVE_STATUS,
            confidence=0.98,
            fast_path_eligible=True,
            entities={"query_type": "SYSTEM_SUMMARY"}
        )

    # 13. ARCHITECTURE / DOCUMENTATION / EXPLANATION
    if "how does prahari work" in q or "explain multi-sensor fusion" in q or "explain sensor trust" in q or "architecture" in q or "documentation" in q or "how does" in q or "explain" in q:
        return IntentMatch(
            intent=INTENT_DOCUMENTATION_QUERY,
            confidence=0.90,
            fast_path_eligible=False,  # Routes through local RAG
            entities={"search_query": query}
        )

    # Default to general status or unknown
    return IntentMatch(
        intent=INTENT_UNKNOWN,
        confidence=0.50,
        fast_path_eligible=False,
        entities={"raw_query": query}
    )
