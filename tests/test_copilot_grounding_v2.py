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
async def test_grounded_copilot_cites_persisted_internal_evidence_ids():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:r=await c.post("/api/copilot/grounded",headers=HEADERS,json={"query":"What is persisted for JALA-01?"})
    body=r.json();assert body["grounded"] is True and body["evidence_ids"]
    assert all(x.startswith(("TEL-","RISK-","ALERT-")) for x in body["evidence_ids"])
    assert body["claims"][0]["evidence_id"] in body["evidence_ids"]
@pytest.mark.asyncio
async def test_grounded_copilot_abstains_instead_of_inventing_operational_claims():
    query="Give the live government provider rainfall, predicted route and official SMS delivery state"
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:r=await c.post("/api/copilot/grounded",headers=HEADERS,json={"query":query})
    body=r.json();assert body=={"grounded":False,"answer":"INSUFFICIENT_PERSISTED_EVIDENCE","claims":[],"evidence_ids":[]}
    assert "delivered" not in body["answer"].lower()

@pytest.mark.asyncio
async def test_grounded_copilot_does_not_answer_unsupported_claim_from_node_telemetry():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        r=await c.post("/api/copilot/grounded",headers=HEADERS,json={"query":"Was the official SMS delivered for JALA-01?"})
    assert r.json()=={"grounded":False,"answer":"INSUFFICIENT_PERSISTED_EVIDENCE","claims":[],"evidence_ids":[]}
