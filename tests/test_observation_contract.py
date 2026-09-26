from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.main import app
from backend.app.services.telemetry_service import telemetry_service


AUTH_HEADERS = {
    "Authorization": f"Bearer {create_access_token({'sub': 'admin', 'role': 'ADMIN', 'dev_auth_bypass': True})}"
}


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    import asyncio

    asyncio.run(seed_data())


@pytest.mark.asyncio
async def test_legacy_telemetry_creates_canonical_observations():
    telemetry_service.reset_sequence_tracking()
    payload = {
        "version": 1,
        "node_id": "JALA-01",
        "sequence": 930001,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {"water_level_cm": 52.5, "rain_intensity": 3.0},
        "rssi": -72,
        "battery_pct": 91.0,
        "source_mode": "SIMULATION",
        "transport": "TEST",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        ingest = await client.post(
            "/api/telemetry/ingest", json=payload, headers=AUTH_HEADERS
        )
        observations = await client.get(
            "/api/interop/sensorthings/Observations",
            params={"node_id": "JALA-01", "sequence_number": 930001},
            headers=AUTH_HEADERS,
        )

    assert ingest.status_code == 200
    assert observations.status_code == 200
    body = observations.json()
    assert body["@iot.count"] == 2
    by_property = {item["observed_property"]: item for item in body["value"]}
    water = by_property["water_level_cm"]
    assert water["domain"] == "JALA"
    assert water["value"] == 52.5
    assert water["unit"] == "cm"
    assert water["provenance"] == "SIMULATION"
    assert water["sequence_number"] == 930001
    assert water["raw_payload_hash"]
    assert water["timestamp"] <= water["received_at"]
    assert water["freshness_seconds"] >= 0


@pytest.mark.asyncio
async def test_sensorthings_things_exposes_truthful_node_provenance():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/interop/sensorthings/Things", headers=AUTH_HEADERS
        )

    assert response.status_code == 200
    by_id = {item["@iot.id"]: item for item in response.json()["value"]}
    assert by_id["VAYU-04"]["properties"]["provenance"] in {
        "SIMULATION", "PLANNED"
    }
    assert by_id["VAYU-04"]["properties"]["hardware_state"] != "CONNECTED"
