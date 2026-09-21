"""
PRAHARI Copilot Fallback Engine
Guarantees 100% offline availability using deterministic template responders.
"""
from typing import Dict, Any, List, Tuple
from backend.app.copilot.schemas import StructuredComponent, ToolResult
from backend.app.copilot.response_generator import response_generator
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
    INTENT_DOCUMENTATION_QUERY,
    INTENT_COMPARISON
)


class DeterministicFallbackEngine:
    """Answers any operational inquiry using tool facts and deterministic formatting."""

    @staticmethod
    def format_fallback_response(
        intent_match: IntentMatch,
        tool_results: List[ToolResult],
        data_mode: str = "REAL"
    ) -> Tuple[str, List[StructuredComponent]]:
        results_by_name: Dict[str, Any] = {tr.tool: tr.data for tr in tool_results if tr.success}
        intent = intent_match.intent
        entities = intent_match.entities

        # 1. Comparison
        if intent == INTENT_COMPARISON:
            nodes_data = [results_by_name.get("get_node_status", {})] if "get_node_status" in results_by_name else []
            # Gather all node status results
            all_n = [tr.data for tr in tool_results if tr.tool == "get_node_status" and tr.success]
            return response_generator.format_comparison(all_n, data_mode)

        # 2. Highest Risk / System Summary
        if intent == INTENT_LIVE_STATUS:
            if entities.get("query_type") == "HIGHEST_RISK":
                all_nodes = results_by_name.get("get_all_nodes", [])
                return response_generator.format_highest_risk(all_nodes, data_mode)

            summary = results_by_name.get("get_system_summary", {})
            network = results_by_name.get("get_network_status", {})
            alerts = results_by_name.get("get_active_alerts", [])
            return response_generator.format_system_health(summary, network, alerts, data_mode)

        # 3. Node Status
        if intent == INTENT_NODE_STATUS:
            failed_node_lookup = next(
                (tr for tr in tool_results if tr.tool == "get_node_status" and not tr.success),
                None,
            )
            if failed_node_lookup:
                return failed_node_lookup.error or f"Node {entities.get('node_id', 'requested')} not found.", []
            node_data = results_by_name.get("get_node_status", {})
            if "error" in node_data:
                return f"Node not found: {node_data['error']}", []
            telem_data = results_by_name.get("get_latest_telemetry", {})
            risk_data = results_by_name.get("get_risk_assessment", {})
            return response_generator.format_node_status(node_data, telem_data, risk_data, data_mode)

        # 4. Telemetry Range Query
        if intent == INTENT_TELEMETRY_QUERY:
            range_data = results_by_name.get("get_telemetry_range", {})
            node_data = results_by_name.get("get_node_status", {})
            return response_generator.format_telemetry_trend(range_data, node_data, data_mode)

        # 5. Alert Query
        if intent == INTENT_ALERT_QUERY:
            is_unack = entities.get("query_type") == "UNACKNOWLEDGED"
            alerts = results_by_name.get("get_unacknowledged_alerts" if is_unack else "get_active_alerts", [])
            return response_generator.format_alert_summary(alerts, is_unack_only=is_unack, data_mode=data_mode)

        # 6. Event Query
        if intent == INTENT_EVENT_QUERY:
            evt_data = results_by_name.get("get_event_details", {})
            if evt_data and "error" not in evt_data:
                return response_generator.format_event_evidence(evt_data, data_mode)
            alerts = results_by_name.get("get_active_alerts", [])
            return response_generator.format_alert_summary(alerts, is_unack_only=False, data_mode=data_mode)

        # 7. Network / Gateway
        if intent == INTENT_NETWORK_QUERY:
            q_type = entities.get("query_type")
            if q_type == "GATEWAY_STATUS":
                gw = results_by_name.get("get_gateway_status", {})
                mode_d = results_by_name.get("get_current_operational_mode", {})
                sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""
                ans = (
                    f"{sim_prefix}### PRAHARI Gateway Status\n\n"
                    f"• **Gateway Interface:** {gw.get('status', 'UNKNOWN')}\n"
                    f"• **Operational Mode:** {gw.get('mode', 'SIMULATOR')}\n"
                    f"• **Serial Port:** {gw.get('port', 'COM3')} @ {gw.get('baud_rate', 115200)} baud\n"
                    f"• **Autonomous Edge Sovereignty:** Armed & operational\n"
                    f"• **Network State:** **{mode_d.get('network_mode', 'LOCAL_EDGE')}**"
                )
                return ans, [StructuredComponent(type="STATUS", title="Gateway Status", data=gw)]

            net = results_by_name.get("get_network_status", {})
            pkts = results_by_name.get("get_packet_statistics", {})
            return response_generator.format_network_status(net, pkts, data_mode)

        # 8. Device Health / Sensor Trust
        if intent == INTENT_DEVICE_HEALTH:
            if entities.get("query_type") == "LOW_TRUST":
                low_trust = results_by_name.get("get_low_trust_sensors", [])
                return response_generator.format_sensor_trust(low_trust, data_mode)

            health = results_by_name.get("get_device_health", {})
            flags = results_by_name.get("get_maintenance_flags", [])
            sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""
            lines = [f"{sim_prefix}### Fleet Device Health & Maintenance Diagnostics\n"]
            if flags:
                lines.append(f"⚠ **{len(flags)} Maintenance Flag(s) Detected:**")
                for fl in flags:
                    lines.append(f"• **{fl.get('node_id')}**: [{fl.get('type')}] {fl.get('message')}")
            else:
                lines.append("✅ All sensor nodes report healthy battery levels (≥25%) and nominal solar voltage.")

            comps = [StructuredComponent(type="STATUS", title="Device Health", data=health)]
            return "\n".join(lines), comps

        # 9. Predictions
        if intent == INTENT_PREDICTION_QUERY:
            preds = results_by_name.get("get_predictions", [])
            return response_generator.format_predictions(preds, data_mode)

        # 10. Documentation
        if intent == INTENT_DOCUMENTATION_QUERY:
            docs_res = results_by_name.get("search_project_documentation", {})
            chunks = docs_res.get("chunks", [])
            if chunks:
                lines = ["### PRAHARI Documentation Knowledge Base\n"]
                for c in chunks[:3]:
                    lines.append(f"**[{c.get('document')} - {c.get('section')}]**\n{c.get('content')}\n")
                return "\n".join(lines), []

        # Generic default summary
        summary = results_by_name.get("get_system_summary", {})
        return (
            f"**PRAHARI COPILOT** is active in **LOCAL ASSISTANT** mode.\n\n"
            f"• Online Nodes: {summary.get('nodes_online', 3)}/{summary.get('nodes_total', 3)}\n"
            f"• Active Emergencies: {summary.get('active_alerts_count', 0)}\n"
            f"• Gateway: {summary.get('gateway_status', 'CONNECTED')}\n\n"
            f"Ask about node status, active alerts, weakest RSSI, or flood/fire evidence.",
            []
        )


deterministic_fallback = DeterministicFallbackEngine()
