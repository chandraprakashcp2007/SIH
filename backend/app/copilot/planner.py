"""
PRAHARI Copilot Query Planner
Determines tool invocation plans for deterministic fast paths and complex inquiries.
"""
from typing import List, Dict, Any
from backend.app.copilot.intent import (
    IntentMatch,
    INTENT_LIVE_STATUS,
    INTENT_NODE_STATUS,
    INTENT_TELEMETRY_QUERY,
    INTENT_ALERT_QUERY,
    INTENT_EVENT_QUERY,
    INTENT_NETWORK_QUERY,
    INTENT_DEVICE_HEALTH,
    INTENT_PREDICTION_QUERY,
    INTENT_ANALYTICS_QUERY,
    INTENT_DOCUMENTATION_QUERY,
    INTENT_COMPARISON,
    INTENT_UNKNOWN
)


class QueryPlanner:
    """Plans minimal concurrent tool calls required to ground each query."""

    @staticmethod
    def plan_tools_for_intent(match: IntentMatch) -> List[Dict[str, Any]]:
        intent = match.intent
        entities = match.entities

        # 1. Comparison
        if intent == INTENT_COMPARISON:
            nodes = entities.get("nodes", ["JALA-01", "BHUMI-03"])
            return [{"name": "get_node_status", "arguments": {"node_id": nid}} for nid in nodes]

        # 2. Node Status / Why critical
        if intent == INTENT_NODE_STATUS:
            node_id = entities.get("node_id", "JALA-01")
            return [
                {"name": "get_node_status", "arguments": {"node_id": node_id}},
                {"name": "get_latest_telemetry", "arguments": {"node_id": node_id}},
                {"name": "get_risk_assessment", "arguments": {"node_id": node_id}}
            ]

        # 3. Telemetry Range Query
        if intent == INTENT_TELEMETRY_QUERY:
            node_id = entities.get("node_id", "JALA-01")
            win = entities.get("window_minutes", 10)
            return [
                {"name": "get_telemetry_range", "arguments": {"node_id": node_id, "minutes": win}},
                {"name": "get_node_status", "arguments": {"node_id": node_id}}
            ]

        # 4. Alert Query
        if intent == INTENT_ALERT_QUERY:
            if entities.get("query_type") == "UNACKNOWLEDGED":
                return [{"name": "get_unacknowledged_alerts", "arguments": {}}]
            return [{"name": "get_active_alerts", "arguments": {}}]

        # 5. Event Evidence Query
        if intent == INTENT_EVENT_QUERY:
            evt_id = entities.get("event_id")
            if evt_id:
                return [{"name": "get_event_details", "arguments": {"event_id": evt_id}}]
            # Fallback to recent events or latest active alert
            return [{"name": "get_active_alerts", "arguments": {}}, {"name": "get_recent_events", "arguments": {"limit": 5}}]

        # 6. Network & Gateway Queries
        if intent == INTENT_NETWORK_QUERY:
            q_type = entities.get("query_type")
            if q_type == "GATEWAY_STATUS":
                return [
                    {"name": "get_gateway_status", "arguments": {}},
                    {"name": "get_current_operational_mode", "arguments": {}}
                ]
            return [
                {"name": "get_network_status", "arguments": {}},
                {"name": "get_packet_statistics", "arguments": {}}
            ]

        # 7. Device Health / Sensor Trust
        if intent == INTENT_DEVICE_HEALTH:
            q_type = entities.get("query_type")
            if q_type == "LOW_TRUST":
                return [{"name": "get_low_trust_sensors", "arguments": {}}]
            return [
                {"name": "get_device_health", "arguments": {}},
                {"name": "get_maintenance_flags", "arguments": {}}
            ]

        # 8. Prediction Query
        if intent == INTENT_PREDICTION_QUERY:
            return [{"name": "get_predictions", "arguments": {}}]

        # 9. System Summary & Highest Risk
        if intent == INTENT_LIVE_STATUS:
            q_type = entities.get("query_type")
            if q_type == "HIGHEST_RISK":
                return [{"name": "get_all_nodes", "arguments": {}}]
            # Comprehensive health check runs in parallel!
            return [
                {"name": "get_system_summary", "arguments": {}},
                {"name": "get_network_status", "arguments": {}},
                {"name": "get_active_alerts", "arguments": {}}
            ]

        # 10. Documentation
        if intent == INTENT_DOCUMENTATION_QUERY:
            query_str = entities.get("search_query", "")
            return [{"name": "search_project_documentation", "arguments": {"query": query_str, "top_k": 3}}]

        # Default fallback
        return [{"name": "get_system_summary", "arguments": {}}]


query_planner = QueryPlanner()
