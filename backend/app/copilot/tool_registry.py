"""
PRAHARI Copilot Tool Registry
Central catalog of all grounded operational tools with metadata, schemas, and handlers.
"""
from typing import Dict, Any, Callable, List, Optional
import inspect

from backend.app.copilot.tools import (
    get_system_summary,
    get_current_operational_mode,
    get_system_readiness,
    get_demo_mode_status,
    get_node_status,
    get_all_nodes,
    get_latest_telemetry,
    get_telemetry_range,
    get_active_alerts,
    get_unacknowledged_alerts,
    get_alert_details,
    get_risk_assessment,
    get_event_details,
    get_recent_events,
    get_predictions,
    get_sensor_trust,
    get_low_trust_sensors,
    get_network_status,
    get_gateway_status,
    get_packet_statistics,
    get_device_health,
    get_maintenance_flags,
    get_analytics_summary,
    search_project_documentation,
    get_current_user_permissions,
    get_operator_briefing
)


class ToolDefinition:
    def __init__(
        self,
        name: str,
        handler: Callable,
        description: str,
        parameters: Dict[str, Any],
        cache_ttl_sec: float = 2.0,
        requires_db: bool = True
    ):
        self.name = name
        self.handler = handler
        self.description = description
        self.parameters = parameters
        self.cache_ttl_sec = cache_ttl_sec
        self.requires_db = requires_db

    def to_openai_tool(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class ToolRegistry:
    """Manages available operational inquiry tools."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_all_default_tools()

    def register(self, tool_def: ToolDefinition):
        self._tools[tool_def.name] = tool_def

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tool_names(self) -> List[str]:
        return list(self._tools.keys())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        return [t.to_openai_tool() for t in self._tools.values()]

    def _register_all_default_tools(self):
        # 1. System Summary
        self.register(ToolDefinition(
            name="get_system_summary",
            handler=get_system_summary,
            description="Retrieve overall platform metrics (node count, active alerts, gateway status, fleet average risk).",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=2.0
        ))

        # 2. Operational Mode
        self.register(ToolDefinition(
            name="get_current_operational_mode",
            handler=get_current_operational_mode,
            description="Check if PRAHARI is running online or in autonomous LOCAL EDGE mode without internet.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=2.0
        ))

        # 3. Node Status
        self.register(ToolDefinition(
            name="get_node_status",
            handler=get_node_status,
            description="Retrieve detailed status, current risk score, band, and explanation for a node (JALA-01, AGNI-02, BHUMI-03, VAYU-04, AKASHA-05).",
            parameters={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Node identifier: JALA-01, AGNI-02, BHUMI-03, VAYU-04, or AKASHA-05"}
                },
                "required": ["node_id"]
            },
            cache_ttl_sec=1.5
        ))

        # 4. All Nodes
        self.register(ToolDefinition(
            name="get_all_nodes",
            handler=get_all_nodes,
            description="List status, battery, RSSI, and current risk band for all 3 nodes.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=2.0
        ))

        # 5. Latest Telemetry
        self.register(ToolDefinition(
            name="get_latest_telemetry",
            handler=get_latest_telemetry,
            description="Retrieve the latest physical sensor readings for a specific node.",
            parameters={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Node identifier: JALA-01, AGNI-02, BHUMI-03, VAYU-04, or AKASHA-05"}
                },
                "required": ["node_id"]
            },
            cache_ttl_sec=1.0
        ))

        # 6. Telemetry Range
        self.register(ToolDefinition(
            name="get_telemetry_range",
            handler=get_telemetry_range,
            description="Retrieve statistical telemetry trend over a temporal window (min, max, average, rate of change).",
            parameters={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Node identifier"},
                    "minutes": {"type": "integer", "description": "Duration in minutes (e.g. 5, 10, 30)", "default": 10},
                    "metric_key": {"type": "string", "description": "Optional specific metric name"}
                },
                "required": ["node_id"]
            },
            cache_ttl_sec=3.0
        ))

        # 7. Risk Assessment
        self.register(ToolDefinition(
            name="get_risk_assessment",
            handler=get_risk_assessment,
            description="Retrieve the authoritative calculated risk score, contributing factors, and explanation for a node.",
            parameters={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Node identifier"}
                },
                "required": ["node_id"]
            },
            cache_ttl_sec=1.5
        ))

        # 8. Active Alerts
        self.register(ToolDefinition(
            name="get_active_alerts",
            handler=get_active_alerts,
            description="Retrieve list of all active (NEW, ACKNOWLEDGED, MONITORING) emergency alerts.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=1.5
        ))

        # 9. Unacknowledged Alerts
        self.register(ToolDefinition(
            name="get_unacknowledged_alerts",
            handler=get_unacknowledged_alerts,
            description="Retrieve list of unacknowledged emergency alerts requiring operator action.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=1.5
        ))

        # 10. Alert Details
        self.register(ToolDefinition(
            name="get_alert_details",
            handler=get_alert_details,
            description="Retrieve full incident evidence and details for a specific alert ID.",
            parameters={
                "type": "object",
                "properties": {
                    "alert_id": {"type": "string", "description": "Alert ID (e.g. ALT-XXXX)"}
                },
                "required": ["alert_id"]
            },
            cache_ttl_sec=3.0
        ))

        # 11. Event Details
        self.register(ToolDefinition(
            name="get_event_details",
            handler=get_event_details,
            description="Retrieve details for a specific event or audit record ID.",
            parameters={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID"}
                },
                "required": ["event_id"]
            },
            cache_ttl_sec=3.0
        ))

        # 12. Recent Events
        self.register(ToolDefinition(
            name="get_recent_events",
            handler=get_recent_events,
            description="Retrieve chronological log of recent platform and disaster events.",
            parameters={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max events to retrieve", "default": 10}
                }
            },
            cache_ttl_sec=3.0
        ))

        # 13. Predictions
        self.register(ToolDefinition(
            name="get_predictions",
            handler=get_predictions,
            description="Retrieve hazard trajectory forecast and threshold crossing time projections.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=2.0
        ))

        # 14. Sensor Trust
        self.register(ToolDefinition(
            name="get_sensor_trust",
            handler=get_sensor_trust,
            description="Retrieve reliability scores (0-100%) for active transducers across nodes.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=2.0
        ))

        # 15. Low Trust Sensors
        self.register(ToolDefinition(
            name="get_low_trust_sensors",
            handler=get_low_trust_sensors,
            description="List any sensors currently flagged with degraded trust (<80%) due to anomalies.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=2.0
        ))

        # 16. Network Status
        self.register(ToolDefinition(
            name="get_network_status",
            handler=get_network_status,
            description="Retrieve RF topology statistics, weakest RSSI node, and average packet loss.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=2.0
        ))

        # 17. Gateway Status
        self.register(ToolDefinition(
            name="get_gateway_status",
            handler=get_gateway_status,
            description="Check physical LoRa concentrator serial port, baud rate, and connection state.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=2.0
        ))

        # 18. Packet Statistics
        self.register(ToolDefinition(
            name="get_packet_statistics",
            handler=get_packet_statistics,
            description="Retrieve packet delivery rate, sequence gaps, and duplicate frame counts.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=2.0
        ))

        # 19. Device Health
        self.register(ToolDefinition(
            name="get_device_health",
            handler=get_device_health,
            description="Retrieve battery voltage, solar power, and diagnostics for all nodes.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=3.0
        ))

        # 20. Maintenance Flags
        self.register(ToolDefinition(
            name="get_maintenance_flags",
            handler=get_maintenance_flags,
            description="Identify nodes needing battery servicing, antenna alignment, or sensor check.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=3.0
        ))

        # 21. Analytics Summary
        self.register(ToolDefinition(
            name="get_analytics_summary",
            handler=get_analytics_summary,
            description="Retrieve macro-level statistics on incident frequencies and dispatch acknowledgement times.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=4.0
        ))

        # 22. System Readiness
        self.register(ToolDefinition(
            name="get_system_readiness",
            handler=get_system_readiness,
            description="Health diagnostic check across backend, database, gateway, and risk engines.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=2.0
        ))

        # 23. Documentation Search
        self.register(ToolDefinition(
            name="search_project_documentation",
            handler=search_project_documentation,
            description="Search local knowledge base for architectural specs, node sensors, algorithms, or guides.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Documentation search query"}
                },
                "required": ["query"]
            },
            cache_ttl_sec=120.0,
            requires_db=False
        ))

        # 24. Demo Mode Status
        self.register(ToolDefinition(
            name="get_demo_mode_status",
            handler=get_demo_mode_status,
            description="Check the current SIH disaster simulation scenario and tick count.",
            parameters={"type": "object", "properties": {}},
            cache_ttl_sec=1.5
        ))

        # 25. User Permissions
        self.register(ToolDefinition(
            name="get_current_user_permissions",
            handler=get_current_user_permissions,
            description="Check current user role and verify read-only boundaries.",
            parameters={
                "type": "object",
                "properties": {
                    "role": {"type": "string", "default": "OPERATOR"}
                }
            },
            cache_ttl_sec=60.0,
            requires_db=False
        ))


tool_registry = ToolRegistry()
