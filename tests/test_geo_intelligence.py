import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.main import app


AUTH_HEADERS = {
    "Authorization": f"Bearer {create_access_token({'sub': 'admin', 'role': 'ADMIN', 'dev_auth_bypass': True})}"
}


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    asyncio.run(seed_data())


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", ["JALA", "AGNI", "BHUMI", "VAYU", "AKASHA"])
async def test_domain_map_returns_backend_derived_geojson(domain):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/geo/domains/{domain}", headers=AUTH_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == domain
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 1
    feature = body["features"][0]
    assert feature["geometry"]["type"] == "Point"
    assert feature["properties"]["risk_band"] in {
        "SAFE", "WATCH", "WARNING", "CRITICAL", "NO_DATA"
    }
    assert feature["properties"]["provenance"] in {
        "REAL", "SIMULATION", "REPLAY", "PLANNED"
    }
    assert body["layers"]
    assert all(layer["status"] in {
        "AVAILABLE", "NOT_CONFIGURED", "NO_LIVE_DATA", "PLANNED"
    } for layer in body["layers"])


@pytest.mark.asyncio
async def test_geo_dataset_registry_never_claims_unconfigured_dem_or_firms():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/geo/datasets", headers=AUTH_HEADERS)

    assert response.status_code == 200
    by_id = {item["id"]: item for item in response.json()}
    assert by_id["NASA_FIRMS"]["status"] == "NOT_CONFIGURED"
    assert by_id["DEM_TERRAIN"]["status"] == "NOT_CONFIGURED"
    assert by_id["NASA_FIRMS"]["provenance"] == "EXTERNAL_DATA"
    assert by_id["DEM_TERRAIN"]["checksum"] is None
