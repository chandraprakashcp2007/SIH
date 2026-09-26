import asyncio
from xml.etree import ElementTree as ET
import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.core.database import AsyncSessionLocal
from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.main import app
from backend.app.models.alerts import Alert

HEADERS={"Authorization":f"Bearer {create_access_token({'sub':'admin','role':'ADMIN','dev_auth_bypass':True})}"}
ALERT_ID="ALT-CAP-TEST"
@pytest.fixture(scope="module",autouse=True)
def setup():
    async def go():
        await seed_data()
        async with AsyncSessionLocal() as db:
            db.add(Alert(id=ALERT_ID,severity="WARNING",hazard="FLOOD",node_id="JALA-01",location_name="Test district",confidence=80,risk_score=70,headline="Flood warning",summary="Water level warning.",action_recommended="Follow local authority instructions.",evidence={"provenance":"SIMULATION"}))
            await db.commit()
    asyncio.run(go())

@pytest.mark.asyncio
async def test_cap_12_xml_contains_required_contract_and_multilingual_info():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        r=await client.post(f"/api/cap/alerts/{ALERT_ID}/export",headers=HEADERS,json={"languages":["en-IN","hi-IN"]})
    assert r.status_code==200
    body=r.json();root=ET.fromstring(body["xml"]);ns={"c":"urn:oasis:names:tc:emergency:cap:1.2"}
    for field in ("identifier","sender","sent","status","msgType","scope"):
        assert root.find(f"c:{field}",ns) is not None
    assert len(root.findall("c:info",ns))==2
    assert body["provenance"]=="SIMULATION"
    assert body["label"]=="CAP-compatible interoperability export"

@pytest.mark.asyncio
async def test_delivery_proof_stays_not_configured_without_provider():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        r=await client.post(f"/api/cap/alerts/{ALERT_ID}/deliver",headers=HEADERS,json={"channel":"SMS"})
    assert r.status_code==200
    assert r.json()["state"]=="NOT_CONFIGURED"
    assert r.json()["provider_message_id"] is None
    assert r.json()["delivered_at"] is None
