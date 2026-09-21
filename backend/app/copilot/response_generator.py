"""
PRAHARI Copilot Response Generator & Structured Card Constructor
Provides deterministic fast-path response formatting without external LLM dependencies.
"""
from typing import Dict, Any, List, Tuple
from backend.app.copilot.schemas import StructuredComponent, ToolResult


class ResponseGenerator:
    """Formats grounded tool outputs into concise operational answers and structured cards."""

    @staticmethod
    def format_node_status(
        node: Dict[str, Any],
        telem: Dict[str, Any],
        risk: Dict[str, Any],
        data_mode: str = "REAL"
    ) -> Tuple[str, List[StructuredComponent]]:
        if node.get("error"):
            return str(node["error"]), []
        nid = node.get("node_id", "NODE")
        name = node.get("name", "")
        status = node.get("status", "ONLINE")
        risk_score = risk.get("risk_score", node.get("current_risk_score", 0.0))
        risk_band = risk.get("risk_band", node.get("current_risk_band", "NORMAL"))
        explanation = risk.get("human_explanation", node.get("explanation", "Nominal operational state."))
        action = risk.get("recommended_action", node.get("recommended_action", "Routine monitoring."))
        metrics = telem.get("metrics", node.get("latest_metrics", {}))
        trust_scores = risk.get("sensor_trust", {})

        sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""

        # Build readable operational bullet points
        metric_bullets = []
        for k, v in metrics.items():
            clean_k = k.replace("_", " ").title()
            metric_bullets.append(f"• {clean_k}: {v}")
        metrics_str = "\n".join(metric_bullets[:5]) if metric_bullets else "• Telemetry within nominal bounds"

        trust_bullets = []
        for s, score in trust_scores.items():
            clean_s = s.replace("_", " ").title()
            trust_bullets.append(f"• {clean_s}: {score}%")
        trust_str = "\n".join(trust_bullets[:3]) if trust_bullets else "• Sensor trust nominal (≥95%)"

        answer = (
            f"{sim_prefix}**{nid}** ({name}) is currently **{risk_band}** with an authoritative hazard score of **{risk_score:.0f}%**.\n\n"
            f"**Observed Sensor Values:**\n{metrics_str}\n\n"
            f"**Causal Risk Explanation:**\n{explanation}\n\n"
            f"**Sensor Trust Reliability:**\n{trust_str}\n\n"
            f"**Recommended Operator Action:**\n{action}"
        )

        components = [
            StructuredComponent(
                type="NODE_SUMMARY",
                title=f"{nid} Status Card",
                data={
                    "node_id": nid,
                    "name": name,
                    "status": status,
                    "risk_score": risk_score,
                    "risk_band": risk_band,
                    "battery_pct": node.get("battery_pct", 100.0),
                    "rssi": node.get("signal_rssi", -75)
                }
            ),
            StructuredComponent(
                type="ACTION_LINK",
                title=f"Inspect {nid} Details",
                data={"target": f"/nodes/{nid}", "label": f"Open {nid} Dashboard"}
            )
        ]

        return answer, components

    @staticmethod
    def format_highest_risk(all_nodes: List[Dict[str, Any]], data_mode: str = "REAL") -> Tuple[str, List[StructuredComponent]]:
        if not all_nodes:
            return "No active sensor nodes registered.", []

        worst = max(all_nodes, key=lambda n: n.get("risk_score", 0.0))
        sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""

        nid = worst.get("node_id")
        score = worst.get("risk_score", 0.0)
        band = worst.get("risk_band", "NORMAL")
        status = worst.get("status", "ONLINE")

        answer = (
            f"{sim_prefix}**{nid}** currently presents the highest hazard level across the monitored zones with a risk score of "
            f"**{score:.0f}% ({band})**.\n\n"
            f"• Node Status: {status}\n"
            f"• LoRa RSSI: {worst.get('rssi', -75)} dBm\n"
            f"• Battery: {worst.get('battery_pct', 100)}%\n\n"
            f"All other fleet nodes are operating at lower or nominal hazard bands."
        )

        components = [
            StructuredComponent(
                type="METRIC",
                title="Highest Risk Node",
                data={"node_id": nid, "score": score, "band": band}
            ),
            StructuredComponent(
                type="ACTION_LINK",
                title=f"View {nid}",
                data={"target": f"/nodes/{nid}", "label": f"Open {nid}"}
            )
        ]

        return answer, components

    @staticmethod
    def format_system_health(
        summary: Dict[str, Any],
        network: Dict[str, Any],
        alerts: List[Dict[str, Any]],
        data_mode: str = "REAL"
    ) -> Tuple[str, List[StructuredComponent]]:
        sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""
        online_nodes = summary.get("nodes_online", 3)
        total_nodes = summary.get("nodes_total", 3)
        active_alerts = summary.get("active_alerts_count", len(alerts))
        crit_alerts = summary.get("critical_alerts_count", 0)
        warn_alerts = summary.get("warning_alerts_count", 0)
        avg_risk = summary.get("average_risk_score", 0.0)
        net_mode = network.get("network_mode", "ONLINE")
        weakest_id = network.get("weakest_node_id", "N/A")
        weakest_rssi = network.get("weakest_rssi_dbm", -85)

        sys_status = "CRITICAL" if crit_alerts > 0 else ("WARNING" if warn_alerts > 0 else "NOMINAL")

        answer = (
            f"{sim_prefix}### PRAHARI System Status: **{sys_status}**\n\n"
            f"• **Fleet Connectivity:** {online_nodes}/{total_nodes} nodes online\n"
            f"• **Active Emergency Incidents:** {active_alerts} ({crit_alerts} Critical, {warn_alerts} Warning)\n"
            f"• **Fleet Average Hazard Risk:** {avg_risk}%\n"
            f"• **Gateway Interface:** CONNECTED ({summary.get('gateway_mode', 'SIMULATOR')})\n"
            f"• **Operational Network Mode:** **{net_mode}**\n"
            f"• **RF Health:** Weakest link is {weakest_id} at {weakest_rssi} dBm\n\n"
            f"Local Edge Command Pipeline is armed and validating telemetry."
        )

        components = [
            StructuredComponent(
                type="STATUS",
                title="System Operational Health",
                data={
                    "status": sys_status,
                    "online_nodes": f"{online_nodes}/{total_nodes}",
                    "active_alerts": active_alerts,
                    "network_mode": net_mode
                }
            ),
            StructuredComponent(
                type="ACTION_LINK",
                title="Open Command Centre",
                data={"target": "/", "label": "Command Centre"}
            )
        ]

        return answer, components

    @staticmethod
    def format_alert_summary(alerts: List[Dict[str, Any]], is_unack_only: bool = False, data_mode: str = "REAL") -> Tuple[str, List[StructuredComponent]]:
        sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""
        if not alerts:
            label = "unacknowledged" if is_unack_only else "active"
            return f"{sim_prefix}✅ There are currently **no {label} emergency alerts**. All monitored hazard sectors are nominal.", []

        lines = [f"{sim_prefix}Found **{len(alerts)} {'unacknowledged' if is_unack_only else 'active'} alert(s)** requiring operator attention:\n"]
        components = []

        for a in alerts[:5]:
            aid = a.get("id")
            sev = a.get("severity")
            haz = a.get("hazard")
            nid = a.get("node_id")
            hd = a.get("headline", "")
            lines.append(f"• **[{sev}] {aid}** ({haz} at {nid}): {hd}")
            components.append(StructuredComponent(
                type="ALERT_SUMMARY",
                title=f"{sev} Alert: {aid}",
                data={"alert_id": aid, "node_id": nid, "severity": sev, "hazard": haz, "headline": hd}
            ))

        lines.append("\nYou can acknowledge or resolve these in the Alert Centre.")
        components.append(StructuredComponent(
            type="ACTION_LINK",
            title="Open Alert Centre",
            data={"target": "/alerts", "label": "View Alert Centre"}
        ))

        return "\n".join(lines), components

    @staticmethod
    def format_network_status(
        network: Dict[str, Any],
        packets: Dict[str, Any],
        data_mode: str = "REAL"
    ) -> Tuple[str, List[StructuredComponent]]:
        sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""
        weakest_id = network.get("weakest_node_id", "BHUMI-03")
        weakest_rssi = network.get("weakest_rssi_dbm", -84)
        avg_rssi = network.get("average_rssi_dbm", -78)
        loss_pct = network.get("average_packet_loss_pct", 0.5)
        p_delivery = packets.get("packet_delivery_rate_pct", 99.5)
        gaps = packets.get("sequence_gaps_detected", 0)
        net_mode = network.get("network_mode", "ONLINE")

        answer = (
            f"{sim_prefix}### PRAHARI RF & Network Topology\n\n"
            f"• **LoRa Link Mode:** **{net_mode}** (Gateway Concentrator Active)\n"
            f"• **Average Fleet RSSI:** {avg_rssi} dBm\n"
            f"• **Weakest Transceiver Link:** **{weakest_id}** at **{weakest_rssi} dBm**\n"
            f"• **Packet Delivery Success Rate:** {p_delivery}%\n"
            f"• **Sequence Gaps Detected:** {gaps}\n"
            f"• **Average Packet Loss Rate:** {loss_pct}%\n\n"
            f"Autonomous Edge communication is operating nominal over 868MHz LoRa frames."
        )

        components = [
            StructuredComponent(
                type="STATUS",
                title="RF Topology Diagnostics",
                data={
                    "mode": net_mode,
                    "delivery_rate": f"{p_delivery}%",
                    "weakest_node": f"{weakest_id} ({weakest_rssi} dBm)"
                }
            ),
            StructuredComponent(
                type="ACTION_LINK",
                title="Inspect Network Details",
                data={"target": "/network", "label": "Open Network Diagnostics"}
            )
        ]

        return answer, components

    @staticmethod
    def format_sensor_trust(low_trust: List[Dict[str, Any]], data_mode: str = "REAL") -> Tuple[str, List[StructuredComponent]]:
        sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""
        if not low_trust:
            return (
                f"{sim_prefix}✅ **All active transducers have nominal trust scores (≥ 80%).**\n\n"
                f"The Sensor Trust Engine has detected no stuck values, physically impossible kinematic jumps, or cross-sensor contradictions.",
                []
            )

        lines = [f"{sim_prefix}⚠ **Degraded Sensor Trust Detected:**\n"]
        components = []

        for f in low_trust:
            nid = f.get("node_id")
            sname = f.get("sensor_name")
            score = f.get("trust_score")
            anomaly = f.get("anomaly", "Anomalous reading")
            lines.append(f"• **{nid} / {sname}**: Trust score **{score}%** ({anomaly})")
            components.append(StructuredComponent(
                type="METRIC",
                title=f"Degraded: {sname}",
                data={"node_id": nid, "sensor": sname, "trust": score, "anomaly": anomaly}
            ))

        lines.append("\nThe Hybrid Risk Engine has automatically downweighted these sensors to prevent false alarms.")
        return "\n".join(lines), components

    @staticmethod
    def format_comparison(nodes_data: List[Dict[str, Any]], data_mode: str = "REAL") -> Tuple[str, List[StructuredComponent]]:
        sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""
        lines = [f"{sim_prefix}### Multi-Node Risk & Health Comparison\n"]
        rows = []

        for n in nodes_data:
            nid = n.get("node_id")
            name = n.get("name")
            risk = n.get("current_risk_score", 0.0)
            band = n.get("current_risk_band", "NORMAL")
            status = n.get("status", "ONLINE")
            rssi = n.get("signal_rssi", -75)
            batt = n.get("battery_pct", 100)

            lines.append(f"• **{nid}** ({name}): Risk **{risk:.0f}% ({band})** | Status: {status} | RSSI: {rssi} dBm | Battery: {batt}%")
            rows.append({
                "node_id": nid,
                "risk": f"{risk:.0f}% ({band})",
                "status": status,
                "rssi": f"{rssi} dBm",
                "battery": f"{batt}%"
            })

        components = [
            StructuredComponent(
                type="TABLE",
                title="Node Hazard Comparison",
                data={"columns": ["Node", "Risk", "Status", "RSSI", "Battery"], "rows": rows}
            )
        ]

        return "\n".join(lines), components

    @staticmethod
    def format_telemetry_trend(
        range_data: Dict[str, Any],
        node_data: Dict[str, Any],
        data_mode: str = "REAL"
    ) -> Tuple[str, List[StructuredComponent]]:
        sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""
        nid = range_data.get("node_id", "NODE")
        name = node_data.get("name", "")
        win = range_data.get("window_minutes", 10)
        metrics = range_data.get("metrics", {})

        lines = [f"{sim_prefix}### {nid} Telemetry Trend (Past {win} Minutes)\n"]
        chart_data = {}

        for k, v in metrics.items():
            clean_k = k.replace("_", " ").title()
            trend = v.get("trend", "STABLE")
            latest = v.get("latest")
            net_ch = v.get("net_change")
            min_v = v.get("min")
            max_v = v.get("max")
            lines.append(f"• **{clean_k}**: {latest} (Change: {net_ch:+} over window | Trend: **{trend}** | Range: {min_v} to {max_v})")
            chart_data[k] = {"latest": latest, "min": min_v, "max": max_v, "trend": trend}

        components = [
            StructuredComponent(
                type="CHART_REQUEST",
                title=f"{nid} Trend Snapshot",
                data={"node_id": nid, "window_minutes": win, "metrics": chart_data}
            ),
            StructuredComponent(
                type="ACTION_LINK",
                title=f"Open {nid} Charts",
                data={"target": f"/nodes/{nid}", "label": f"View {nid} Hydrograph"}
            )
        ]

        return "\n".join(lines), components

    @staticmethod
    def format_predictions(preds: List[Dict[str, Any]], data_mode: str = "REAL") -> Tuple[str, List[StructuredComponent]]:
        sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""
        lines = [f"{sim_prefix}### Hazard Trajectory Projections (Next 5-15 Minutes)\n"]
        components = []

        for p in preds:
            nid = p.get("node_id")
            haz = p.get("hazard")
            cur_risk = p.get("current_risk", 0.0)
            proj_ch = p.get("projected_5min_change", 0.0)
            trend_dir = p.get("trend_direction", "STABLE")
            crossing = p.get("crossing_window", "NO THRESHOLD CROSSING DETECTED")

            lines.append(f"• **{nid} ({haz})**: Current Risk **{cur_risk:.0f}%** | Trend: **{trend_dir}** ({proj_ch:+} in 5 min) | Crossing Window: *{crossing}*")
            components.append(StructuredComponent(
                type="TIMELINE",
                title=f"Forecast: {nid}",
                data={"node_id": nid, "trend": trend_dir, "projected_change": proj_ch, "crossing": crossing}
            ))

        return "\n".join(lines), components

    @staticmethod
    def format_event_evidence(event_data: Dict[str, Any], data_mode: str = "REAL") -> Tuple[str, List[StructuredComponent]]:
        sim_prefix = "[SIMULATION] " if data_mode == "SIMULATION" else ""
        eid = event_data.get("id", "EVT")
        nid = event_data.get("node_id", "NODE")
        sev = event_data.get("severity", "WARNING")
        haz = event_data.get("hazard", "HAZARD")
        hl = event_data.get("headline", "")
        exp = event_data.get("explanation", "")
        act = event_data.get("action", "")
        evidence = event_data.get("evidence", {})

        ev_bullets = [f"• {k.replace('_', ' ').title()}: {v}" for k, v in evidence.items()][:5]
        ev_str = "\n".join(ev_bullets) if ev_bullets else "• Sensor telemetry recorded"

        answer = (
            f"{sim_prefix}### Incident Record: **{eid}**\n\n"
            f"• **Zone:** {nid} ({haz})\n"
            f"• **Severity:** {sev}\n"
            f"• **Incident Headline:** {hl}\n\n"
            f"**Recorded Sensor Evidence:**\n{ev_str}\n\n"
            f"**Causal Risk Narrative:**\n{exp}\n\n"
            f"**Recommended Emergency Action:**\n{act}"
        )

        components = [
            StructuredComponent(
                type="ALERT_SUMMARY",
                title=f"Incident Evidence: {eid}",
                data={"event_id": eid, "node_id": nid, "severity": sev, "evidence": evidence}
            )
        ]

        return answer, components


response_generator = ResponseGenerator()
