"""
PRAHARI Copilot Citations & Source Attribution Module
Categorizes operational provenance and renders standardized source chips.
"""
from typing import List, Set, Dict

SOURCE_LIVE_TELEMETRY = "LIVE TELEMETRY"
SOURCE_RISK_ENGINE = "RISK ENGINE"
SOURCE_ALERT_DATABASE = "ALERT DATABASE"
SOURCE_NETWORK_STATUS = "NETWORK STATUS"
SOURCE_DEVICE_HEALTH = "DEVICE HEALTH"
SOURCE_PROJECT_DOCS = "PROJECT DOCS"
SOURCE_SIMULATOR = "SIMULATOR"
SOURCE_SYSTEM_REGISTRY = "SYSTEM REGISTRY"

TOOL_SOURCE_MAPPING = {
    "get_system_summary": [SOURCE_SYSTEM_REGISTRY, SOURCE_ALERT_DATABASE],
    "get_current_operational_mode": [SOURCE_SYSTEM_REGISTRY],
    "get_node_status": [SOURCE_LIVE_TELEMETRY, SOURCE_RISK_ENGINE],
    "get_all_nodes": [SOURCE_SYSTEM_REGISTRY, SOURCE_DEVICE_HEALTH],
    "get_latest_telemetry": [SOURCE_LIVE_TELEMETRY],
    "get_telemetry_range": [SOURCE_LIVE_TELEMETRY],
    "get_risk_assessment": [SOURCE_RISK_ENGINE],
    "get_active_alerts": [SOURCE_ALERT_DATABASE],
    "get_unacknowledged_alerts": [SOURCE_ALERT_DATABASE],
    "get_alert_details": [SOURCE_ALERT_DATABASE, SOURCE_RISK_ENGINE],
    "get_event_details": [SOURCE_ALERT_DATABASE, SOURCE_LIVE_TELEMETRY],
    "get_recent_events": [SOURCE_ALERT_DATABASE],
    "get_predictions": [SOURCE_RISK_ENGINE],
    "get_sensor_trust": [SOURCE_RISK_ENGINE],
    "get_low_trust_sensors": [SOURCE_RISK_ENGINE],
    "get_network_status": [SOURCE_NETWORK_STATUS],
    "get_gateway_status": [SOURCE_NETWORK_STATUS],
    "get_packet_statistics": [SOURCE_NETWORK_STATUS],
    "get_device_health": [SOURCE_DEVICE_HEALTH],
    "get_maintenance_flags": [SOURCE_DEVICE_HEALTH],
    "get_analytics_summary": [SOURCE_ALERT_DATABASE, SOURCE_NETWORK_STATUS],
    "get_system_readiness": [SOURCE_SYSTEM_REGISTRY, SOURCE_DEVICE_HEALTH],
    "search_project_documentation": [SOURCE_PROJECT_DOCS],
    "get_demo_mode_status": [SOURCE_SIMULATOR],
    "get_current_user_permissions": [SOURCE_SYSTEM_REGISTRY]
}


def resolve_sources_from_tools(tools_executed: List[str], is_simulation: bool = False) -> List[str]:
    """Generates unique source tags based on the tools invoked."""
    sources: Set[str] = set()
    for tool_name in tools_executed:
        mapped = TOOL_SOURCE_MAPPING.get(tool_name, [SOURCE_SYSTEM_REGISTRY])
        for s in mapped:
            sources.add(s)

    if is_simulation:
        sources.add(SOURCE_SIMULATOR)

    # Sort deterministically
    ordered_priority = [
        SOURCE_LIVE_TELEMETRY,
        SOURCE_RISK_ENGINE,
        SOURCE_ALERT_DATABASE,
        SOURCE_NETWORK_STATUS,
        SOURCE_DEVICE_HEALTH,
        SOURCE_PROJECT_DOCS,
        SOURCE_SIMULATOR,
        SOURCE_SYSTEM_REGISTRY,
    ]
    return [s for s in ordered_priority if s in sources]
