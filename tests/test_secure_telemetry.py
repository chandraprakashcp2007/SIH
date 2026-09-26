import asyncio,hashlib,hmac,json,os
from datetime import datetime,timezone
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
async def test_signed_ingest_rejects_nonce_replay_without_second_real_mutation(monkeypatch):
    secret="test-device-secret";monkeypatch.setenv("PRAHARI_DEVICE_KEYS",json.dumps({"JALA-01":secret}))
    envelope={"node_id":"JALA-01","nonce":"nonce-secure-1","timestamp":datetime.now(timezone.utc).isoformat(),"payload":{"sequence":88001,"rssi":-70,"battery_pct":90,"metrics":{"water_level_cm":35},"source_mode":"REAL"}}
    canonical=json.dumps(envelope,sort_keys=True,separators=(",",":"));envelope["signature"]=hmac.new(secret.encode(),canonical.encode(),hashlib.sha256).hexdigest()
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        first=await c.post("/api/security/telemetry/ingest",headers=HEADERS,json=envelope)
        async with AsyncSessionLocal() as db:after_first=(await db.execute(select(func.count()).select_from(TelemetryRecord).where(TelemetryRecord.node_id=="JALA-01",TelemetryRecord.source_mode=="REAL"))).scalar_one()
        replay=await c.post("/api/security/telemetry/ingest",headers=HEADERS,json=envelope)
        async with AsyncSessionLocal() as db:after_replay=(await db.execute(select(func.count()).select_from(TelemetryRecord).where(TelemetryRecord.node_id=="JALA-01",TelemetryRecord.source_mode=="REAL"))).scalar_one()
        chain=await c.get("/api/security/audit-chain/verify",headers=HEADERS)
    assert first.status_code==200
    assert replay.status_code==409 and replay.json()["detail"]=="REPLAY_DETECTED"
    assert after_replay==after_first
    assert chain.json()["valid"] is True
@pytest.mark.asyncio
async def test_missing_device_keys_is_not_configured(monkeypatch):
    monkeypatch.delenv("PRAHARI_DEVICE_KEYS",raising=False)
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:r=await c.get("/api/security/status",headers=HEADERS)
    assert r.json()["signed_telemetry"]=="NOT_CONFIGURED"
