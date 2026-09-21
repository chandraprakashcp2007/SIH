"""
Tests for Copilot Tool Registry & Tool Execution
"""
import pytest
import pytest_asyncio
from backend.app.core.database import AsyncSessionLocal
from backend.app.copilot.tool_registry import tool_registry
from backend.app.copilot.tool_executor import tool_executor


REQUIRED_TOOLS = [
    "get_system_summary",
    "get_current_operational_mode",
    "get_node_status",
    "get_all_nodes",
    "get_latest_telemetry",
    "get_telemetry_range",
    "get_risk_assessment",
    "get_active_alerts",
    "get_unacknowledged_alerts",
    "get_alert_details",
    "get_event_details",
    "get_recent_events",
    "get_predictions",
    "get_sensor_trust",
    "get_low_trust_sensors",
    "get_network_status",
    "get_gateway_status",
    "get_packet_statistics",
    "get_device_health",
    "get_maintenance_flags",
    "get_analytics_summary",
    "get_system_readiness",
    "search_project_documentation",
    "get_demo_mode_status",
    "get_current_user_permissions"
]


def test_all_required_tools_registered():
    registered = tool_registry.list_tool_names()
    for tool_name in REQUIRED_TOOLS:
        assert tool_name in registered, f"Required tool '{tool_name}' missing from tool_registry."


@pytest.mark.asyncio
async def test_tool_execution_structured_contract():
    async with AsyncSessionLocal() as db:
        res = await tool_executor.execute_tool("get_system_summary", {}, db=db)
        assert res.success is True
        assert res.tool == "get_system_summary"
        assert res.data_mode in ("REAL", "SIMULATION")
        assert "nodes_total" in res.data
        assert res.data["nodes_total"] >= 3


@pytest.mark.asyncio
async def test_node_status_tool():
    async with AsyncSessionLocal() as db:
        res = await tool_executor.execute_tool("get_node_status", {"node_id": "JALA-01"}, db=db)
        assert res.success is True
        assert res.data["node_id"] == "JALA-01"
        assert "current_risk_score" in res.data


@pytest.mark.asyncio
async def test_parallel_tool_execution():
    async with AsyncSessionLocal() as db:
        plan = [
            {"name": "get_system_summary", "arguments": {}},
            {"name": "get_network_status", "arguments": {}},
            {"name": "get_device_health", "arguments": {}}
        ]
        results = await tool_executor.execute_parallel(plan, db=db)
        assert len(results) == 3
        for r in results:
            assert r.success is True
            assert isinstance(r.data, dict)


@pytest.mark.asyncio
async def test_gateway_tool_reports_derived_freshness():
    async with AsyncSessionLocal() as db:
        res = await tool_executor.execute_tool("get_gateway_status", {}, db=db)
    assert res.success is True
    assert res.data["status"] in {"CONNECTED", "STALE", "OFFLINE"}
    assert "last_packet_age_seconds" in res.data
