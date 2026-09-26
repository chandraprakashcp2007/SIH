from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.main import app
from backend.app.services.telemetry_service import telemetry_service


AUTH_HEADERS = {"Authorization": f"Bearer {create_access_token({'sub': 'admin', 'role': 'ADMIN', 'dev_auth_bypass': True})}"}


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    import asyncio
    asyncio.run(seed_data())


@pytest.mark.asyncio
async def test_observation_aggregation_supports_required_ranges():
    telemetry_service.reset_sequence_tracking()
    payload = {
        "version": 1, "node_id": "JALA-01", "sequence": 940001,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {"water_level_cm": 60.0}, "rssi": -70,
        "battery_pct": 90, "source_mode": "SIMULATION",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.post("/api/telemetry/ingest", json=payload, headers=AUTH_HEADERS)).status_code == 200
        for time_range in ("15m", "1h", "6h", "24h", "7d"):
            response = await client.get(
                "/api/observations/aggregate",
                params={"node_id": "JALA-01", "observed_property": "water_level_cm", "range": time_range},
                headers=AUTH_HEADERS,
            )
            assert response.status_code == 200
            body = response.json()
            assert body["range"] == time_range
            assert body["unit"] == "cm"
            assert body["source"] == "DATABASE_OBSERVATIONS"
            assert body["provenance"] == "SIMULATION"
            assert body["points"]


@pytest.mark.asyncio
async def test_fleet_health_exposes_persisted_status_and_reasons():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/sensor-health", headers=AUTH_HEADERS)

    assert response.status_code == 200
    matching = [item for item in response.json() if item["node_id"] == "JALA-01"]
    assert matching
    assert matching[0]["state"] in {"HEALTHY", "DEGRADED", "SUSPECT", "FAILED", "OFFLINE", "CALIBRATION_DUE"}
    assert isinstance(matching[0]["reason_codes"], list)
    assert 0 <= matching[0]["trust_score"] <= 100
