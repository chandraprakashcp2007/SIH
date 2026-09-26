import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.main import app

HEADERS={"Authorization":f"Bearer {create_access_token({'sub':'admin','role':'ADMIN','dev_auth_bypass':True})}"}
@pytest.fixture(scope="module",autouse=True)
def setup(): asyncio.run(seed_data())

@pytest.mark.asyncio
async def test_twin_keeps_hazard_uncertainty_and_blind_spots_separate():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        r=await client.post("/api/digital-twin/refresh",headers=HEADERS)
    assert r.status_code==200
    body=r.json()
    assert len(body)==5
    assert all("hazard_boundary" in x and "uncertainty_boundary" in x and "blind_spots" in x for x in body)
    assert all(x["blind_spots"] for x in body)
    assert all(x["confidence"] is not None and x["uncertainty"] is not None for x in body)
    assert all(x["provenance"] in {"REAL","SIMULATION","EXTERNAL_DATA","MODEL"} for x in body)
