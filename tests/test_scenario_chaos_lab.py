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
async def real_count():
    async with AsyncSessionLocal() as db:return (await db.execute(select(func.count()).select_from(TelemetryRecord).where(TelemetryRecord.source_mode=="REAL"))).scalar_one()
@pytest.mark.asyncio
async def test_scenario_runs_are_deterministic_and_simulation_isolated():
    before=await real_count();payload={"scenario":"FLOOD_SURGE","seed":42,"parameters":{"rainfall":80}}
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        a=await c.post("/api/lab/scenarios/run",headers=HEADERS,json=payload);b=await c.post("/api/lab/scenarios/run",headers=HEADERS,json=payload)
    assert a.json()["result_digest"]==b.json()["result_digest"]
    assert a.json()["provenance"]=="SIMULATION" and a.json()["operational_mutation"] is False
    assert await real_count()==before
@pytest.mark.asyncio
async def test_chaos_faults_are_confined_to_simulation_run():
    before=await real_count()
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:r=await c.post("/api/lab/chaos/run",headers=HEADERS,json={"seed":7,"faults":["PACKET_LOSS","SENSOR_STUCK"]})
    assert r.json()["provenance"]=="SIMULATION" and r.json()["real_state_strengthened"] is False
    assert r.json()["faults"]==["PACKET_LOSS","SENSOR_STUCK"] and await real_count()==before
