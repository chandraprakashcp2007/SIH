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
async def test_damage_evidence_requires_human_verification_for_verified_state():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:r=await c.post("/api/recovery/evidence",headers=HEADERS,json={"incident_id":"INC-1","kind":"PHOTO_ASSESSMENT","provenance":"EXTERNAL_DATA","description":"Unverified field upload","human_verified":False})
    assert r.json()["verification_state"]=="PENDING_HUMAN_VERIFICATION"
@pytest.mark.asyncio
async def test_incident_report_cites_evidence_and_never_auto_all_clear():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        evidence=await c.get("/api/recovery/evidence?incident_id=INC-1",headers=HEADERS)
        report=await c.post("/api/recovery/reports",headers=HEADERS,json={"incident_id":"INC-1","requested_status":"ALL_CLEAR"})
    assert evidence.json()[0]["id"] in report.json()["evidence_ids"]
    assert report.json()["recovery_status"]=="ASSESSMENT_PENDING"
    assert report.json()["auto_all_clear"] is False
