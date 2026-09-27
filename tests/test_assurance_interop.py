import asyncio
import pytest
from httpx import ASGITransport,AsyncClient
from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.main import app
HEADERS={"Authorization":f"Bearer {create_access_token({'sub':'admin','role':'ADMIN','dev_auth_bypass':True})}"}
@pytest.fixture(scope="module",autouse=True)
def setup():asyncio.run(seed_data())
@pytest.mark.asyncio
async def test_stac_catalog_is_truthful_metadata_not_a_live_data_claim():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:r=await c.get("/api/interop/stac",headers=HEADERS)
    body=r.json();assert body["stac_version"]=="1.0.0" and body["type"]=="Catalog"
    assert body["operational_status"]=="METADATA_ONLY" and body["live_provider_claim"] is False
@pytest.mark.asyncio
async def test_safety_case_and_ddqi_persist_blockers_and_evidence():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        snap=await c.post("/api/assurance/refresh",headers=HEADERS);case=await c.get("/api/assurance/safety-case",headers=HEADERS)
    assert 0<=snap.json()["ddqi"]<=100 and snap.json()["status"]=="CONDITIONAL"
    assert "AUTHORITATIVE_DATASETS_NOT_CONFIGURED" in snap.json()["blockers"]
    assert case.json()["claims"] and all(claim["evidence_ids"] for claim in case.json()["claims"])
    assert case.json()["production_ready"] is False
