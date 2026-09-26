import asyncio
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.main import app

HEADERS = {"Authorization": f"Bearer {create_access_token({'sub':'admin','role':'ADMIN','dev_auth_bypass':True})}"}


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    asyncio.run(seed_data())


@pytest.mark.asyncio
async def test_unconfigured_river_topology_never_invents_travel_time():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        topology = await client.get("/api/jala/topology", headers=HEADERS)
        threats = await client.post("/api/jala/downstream-threats/evaluate", headers=HEADERS)
    assert topology.status_code == 200
    assert topology.json()["status"] == "NOT_CONFIGURED"
    assert threats.status_code == 200
    assert threats.json()["status"] == "NOT_CONFIGURED"
    assert threats.json()["travel_time_minutes"] is None
    assert threats.json()["time_to_impact_state"] == "UNAVAILABLE"
    assert "validated" in threats.json()["reason"].lower()


@pytest.mark.asyncio
async def test_predictions_expose_unavailable_downstream_time_truthfully():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predictions", headers=HEADERS)
    jala = next(item for item in response.json() if item["node_id"] == "JALA-01")
    assert jala["downstream_time_to_impact"] is None
    assert jala["downstream_time_state"] == "UNAVAILABLE"
