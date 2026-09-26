"""
FastAPI REST API Integration Tests
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.db.init_db import seed_data
from backend.app.core.security import create_access_token

AUTH_HEADERS = {"Authorization": f"Bearer {create_access_token({'sub': 'admin', 'role': 'ADMIN', 'dev_auth_bypass': True})}"}


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    import asyncio
    asyncio.run(seed_data())


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "PRAHARI-NET"
        assert data["status"] == "OPERATIONAL"


@pytest.mark.asyncio
async def test_system_summary():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/system/summary", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["nodes_total"] == 5
        assert data["gateway_status"] in {"CONNECTED", "STALE", "OFFLINE"}
        assert "last_packet_age_seconds" in data


@pytest.mark.asyncio
async def test_list_nodes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/nodes", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        nodes = resp.json()
        assert len(nodes) == 5
        node_ids = [n["id"] for n in nodes]
        assert "JALA-01" in node_ids
        assert "AGNI-02" in node_ids
        assert "BHUMI-03" in node_ids


@pytest.mark.asyncio
async def test_telemetry_ingestion():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "version": 1,
            "node_id": "JALA-01",
            "sequence": 501,
            "metrics": {
                "water_level_cm": 42.5,
                "water_distance_cm": 157.5,
                "water_rise_rate_cm_min": 0.2,
                "water_rise_acceleration": 0.01,
                "rain_intensity": 2.0,
                "temperature_c": 28.5
            },
            "rssi": -72,
            "battery_pct": 93.5,
            "is_simulation": True
        }
        resp = await ac.post("/api/telemetry/ingest", json=payload, headers=AUTH_HEADERS)
        assert resp.status_code == 200
        res_data = resp.json()
        assert res_data["status"] == "success"
        assert res_data["node_id"] == "JALA-01"
        assert "risk_score" in res_data
        assert "sensor_trust" in res_data


@pytest.mark.asyncio
async def test_copilot_chat():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/copilot/chat", json={"message": "Which node currently has the highest risk?"}, headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert len(data["reply"]) > 10


@pytest.mark.asyncio
async def test_readiness_and_calibration_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        readiness = await ac.get("/api/readiness", headers=AUTH_HEADERS)
        calibration = await ac.get("/api/calibration", headers=AUTH_HEADERS)
    assert readiness.status_code == 200
    assert {"database", "gateway", "jala", "agni", "bhumi"} <= set(readiness.json()["checks"])
    assert calibration.status_code == 200
    assert {"JALA-01", "AGNI-02", "BHUMI-03"} <= set(calibration.json()["nodes"])

