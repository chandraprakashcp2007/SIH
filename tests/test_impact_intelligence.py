import asyncio
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.main import app

HEADERS = {"Authorization": f"Bearer {create_access_token({'sub':'admin','role':'ADMIN','dev_auth_bypass':True})}"}

@pytest.fixture(scope="module", autouse=True)
def setup_database(): asyncio.run(seed_data())

@pytest.mark.asyncio
async def test_impact_evaluation_withholds_exposure_without_authoritative_assets():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/impact/evaluate", headers=HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NOT_CONFIGURED"
    assert body["population_exposed"] is None
    assert body["assets_exposed"] is None
    assert body["provenance"] == "EXTERNAL_DATA"

@pytest.mark.asyncio
async def test_evacuation_and_safe_zones_never_claim_guaranteed_safety():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        route = await client.post("/api/evacuation/evaluate", headers=HEADERS)
        zones = await client.get("/api/safe-zones", headers=HEADERS)
    assert route.status_code == 200
    assert route.json()["status"] == "NOT_CONFIGURED"
    assert route.json()["guaranteed_safe"] is False
    assert "guarantee" in route.json()["safety_disclaimer"].lower()
    assert zones.status_code == 200
    assert zones.json()["status"] == "NOT_CONFIGURED"
    assert zones.json()["zones"] == []
