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
async def test_queue_is_checksum_idempotent_and_ack_replay_safe():
    payload={"operation":"CAP_EXPORT","body":{"alert_id":"ALT-1"},"provenance":"REAL"}
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        a=await c.post("/api/continuity/queue",headers=HEADERS,json=payload);b=await c.post("/api/continuity/queue",headers=HEADERS,json=payload)
        ack1=await c.post(f"/api/continuity/queue/{a.json()['id']}/ack",headers=HEADERS);ack2=await c.post(f"/api/continuity/queue/{a.json()['id']}/ack",headers=HEADERS)
    assert a.json()["id"]==b.json()["id"]
    assert ack1.json()["state"]==ack2.json()["state"]=="ACKNOWLEDGED"
@pytest.mark.asyncio
async def test_continuity_and_transport_states_are_truthful():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        r=await c.post("/api/continuity/evaluate",headers=HEADERS,json={"internet":False,"gateway":True,"local_wifi":True,"external_data":False,"battery_pct":18})
        t=await c.get("/api/continuity/transports",headers=HEADERS)
    assert r.json()["mode"]=="EXTERNAL_DATA_DEGRADED"
    assert r.json()["energy_policy"]=="CONSERVE"
    states={x["transport"]:x["state"] for x in t.json()}
    assert states["LORA"] in {"PLANNED","UNAVAILABLE"}
    assert states["WIFI"]=="SUPPORTED"
