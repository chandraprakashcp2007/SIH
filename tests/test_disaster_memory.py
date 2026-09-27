import asyncio
import pytest
from httpx import ASGITransport,AsyncClient
from sqlalchemy import func,select
from backend.app.core.database import AsyncSessionLocal
from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.main import app
from backend.app.models.telemetry import TelemetryRecord

HEADERS={"Authorization":f"Bearer {create_access_token({'sub':'admin','role':'ADMIN','dev_auth_bypass':True})}"}
@pytest.fixture(scope="module",autouse=True)
def setup():asyncio.run(seed_data())

@pytest.mark.asyncio
async def test_memory_fingerprint_similarity_and_hash_linked_black_box():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        first=await c.post("/api/memory/events",headers=HEADERS,json={"hazard":"FLOOD","evidence_ids":["OBS-1","RISK-1"],"features":{"band":"WARNING","trend":"RISING"},"provenance":"SIMULATION"})
        second=await c.post("/api/memory/events",headers=HEADERS,json={"hazard":"FLOOD","evidence_ids":["OBS-2"],"features":{"band":"WARNING","trend":"RISING"},"provenance":"SIMULATION"})
        similar=await c.get(f"/api/memory/events/{second.json()['id']}/similar",headers=HEADERS)
        chain=await c.get("/api/memory/black-box/verify",headers=HEADERS)
    assert first.json()["fingerprint"]==second.json()["fingerprint"]
    assert similar.json()[0]["event_id"]==first.json()["id"] and similar.json()[0]["score"]==1.0
    assert chain.json()["valid"] is True and chain.json()["entries"]>=2

@pytest.mark.asyncio
async def test_black_box_replay_never_writes_operational_telemetry():
    async with AsyncSessionLocal() as db:before=(await db.execute(select(func.count()).select_from(TelemetryRecord).where(TelemetryRecord.source_mode=="REAL"))).scalar_one()
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        events=await c.get("/api/memory/events",headers=HEADERS)
        replay=await c.post(f"/api/memory/events/{events.json()[0]['id']}/replay",headers=HEADERS)
    async with AsyncSessionLocal() as db:after=(await db.execute(select(func.count()).select_from(TelemetryRecord).where(TelemetryRecord.source_mode=="REAL"))).scalar_one()
    assert replay.json()["source_mode"]=="REPLAY" and replay.json()["operational_mutation"] is False
    assert after==before
