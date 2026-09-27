import asyncio,hashlib,hmac,json
from datetime import datetime,timedelta,timezone
import pytest
from httpx import ASGITransport,AsyncClient
from sqlalchemy import func,select
from backend.app.core.database import AsyncSessionLocal
from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.main import app
from backend.app.models.telemetry import TelemetryRecord
from backend.app.services.telemetry_service import telemetry_service
HEADERS={"Authorization":f"Bearer {create_access_token({'sub':'admin','role':'ADMIN','dev_auth_bypass':True})}"}
@pytest.fixture(scope="module",autouse=True)
def setup():asyncio.run(seed_data())

def signed_envelope(secret, *, node_id="JALA-01", nonce, sequence, timestamp=None):
    envelope={"node_id":node_id,"nonce":nonce,"timestamp":timestamp or datetime.now(timezone.utc).isoformat(),"payload":{"sequence":sequence,"rssi":-70,"battery_pct":90,"metrics":{"water_level_cm":35},"source_mode":"REAL"}}
    canonical=json.dumps(envelope,sort_keys=True,separators=(",",":"))
    envelope["signature"]=hmac.new(secret.encode(),canonical.encode(),hashlib.sha256).hexdigest()
    return envelope

async def real_count(node_id="JALA-01"):
    async with AsyncSessionLocal() as db:
        return (await db.execute(select(func.count()).select_from(TelemetryRecord).where(TelemetryRecord.node_id==node_id,TelemetryRecord.source_mode=="REAL"))).scalar_one()

async def next_real_sequence(node_id="JALA-01"):
    async with AsyncSessionLocal() as db:
        current=(await db.execute(select(func.max(TelemetryRecord.sequence)).where(TelemetryRecord.node_id==node_id,TelemetryRecord.source_mode=="REAL"))).scalar_one()
    return (current or 0)+1

@pytest.mark.asyncio
async def test_signed_ingest_rejects_nonce_replay_without_second_real_mutation(monkeypatch):
    secret="test-device-secret";monkeypatch.setenv("PRAHARI_DEVICE_KEYS",json.dumps({"JALA-01":secret}))
    telemetry_service.reset_sequence_tracking()
    envelope=signed_envelope(secret,nonce="nonce-secure-1",sequence=await next_real_sequence())
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        first=await c.post("/api/security/telemetry/ingest",headers=HEADERS,json=envelope)
        after_first=await real_count()
        replay=await c.post("/api/security/telemetry/ingest",headers=HEADERS,json=envelope)
        after_replay=await real_count()
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

@pytest.mark.asyncio
async def test_invalid_signature_is_rejected_persisted_and_never_mutates_real(monkeypatch,caplog):
    secret="invalid-signature-secret";monkeypatch.setenv("PRAHARI_DEVICE_KEYS",json.dumps({"JALA-01":secret}))
    envelope=signed_envelope(secret,nonce="nonce-invalid-signature",sequence=88002);envelope["signature"]="0"*64
    before=await real_count()
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        response=await c.post("/api/security/telemetry/ingest",headers=HEADERS,json=envelope)
        events=await c.get("/api/security/events",headers=HEADERS)
    assert response.status_code==401 and response.json()["detail"]=="INVALID_SIGNATURE"
    assert await real_count()==before
    assert any(item["event_type"]=="INVALID_SIGNATURE" and item["node_id"]=="JALA-01" for item in events.json())
    assert secret not in response.text and secret not in events.text and secret not in caplog.text

@pytest.mark.asyncio
async def test_unknown_device_is_rejected_persisted_and_never_mutates_real(monkeypatch,caplog):
    secret="unknown-device-secret";monkeypatch.setenv("PRAHARI_DEVICE_KEYS",json.dumps({"JALA-01":"known-only"}))
    envelope=signed_envelope(secret,node_id="UNKNOWN-99",nonce="nonce-unknown-device",sequence=1)
    before=await real_count("UNKNOWN-99")
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        response=await c.post("/api/security/telemetry/ingest",headers=HEADERS,json=envelope)
        events=await c.get("/api/security/events",headers=HEADERS)
    assert response.status_code==503 and response.json()["detail"]=="DEVICE_KEY_NOT_CONFIGURED"
    assert await real_count("UNKNOWN-99")==before
    assert any(item["event_type"]=="UNKNOWN_DEVICE" and item["node_id"]=="UNKNOWN-99" for item in events.json())
    assert secret not in response.text and secret not in events.text and secret not in caplog.text

@pytest.mark.asyncio
async def test_stale_timestamp_is_rejected_persisted_and_never_mutates_real(monkeypatch,caplog):
    secret="stale-envelope-secret";monkeypatch.setenv("PRAHARI_DEVICE_KEYS",json.dumps({"JALA-01":secret}))
    stale=(datetime.now(timezone.utc)-timedelta(minutes=6)).isoformat()
    envelope=signed_envelope(secret,nonce="nonce-stale-envelope",sequence=88003,timestamp=stale)
    before=await real_count()
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        response=await c.post("/api/security/telemetry/ingest",headers=HEADERS,json=envelope)
        events=await c.get("/api/security/events",headers=HEADERS)
    assert response.status_code==422 and response.json()["detail"]=="STALE_SIGNED_ENVELOPE"
    assert await real_count()==before
    assert any(item["event_type"]=="STALE_SIGNED_ENVELOPE" and item["node_id"]=="JALA-01" for item in events.json())
    assert secret not in response.text and secret not in events.text and secret not in caplog.text

@pytest.mark.asyncio
async def test_fresh_nonce_cannot_replay_sequence_or_mutate_real(monkeypatch,caplog):
    secret="sequence-replay-secret";monkeypatch.setenv("PRAHARI_DEVICE_KEYS",json.dumps({"AGNI-02":secret}))
    telemetry_service.reset_sequence_tracking()
    sequence=await next_real_sequence("AGNI-02")
    first=signed_envelope(secret,node_id="AGNI-02",nonce="nonce-sequence-first",sequence=sequence)
    replay=signed_envelope(secret,node_id="AGNI-02",nonce="nonce-sequence-replay",sequence=sequence)
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as c:
        accepted=await c.post("/api/security/telemetry/ingest",headers=HEADERS,json=first)
        after_first=await real_count("AGNI-02")
        rejected=await c.post("/api/security/telemetry/ingest",headers=HEADERS,json=replay)
        events=await c.get("/api/security/events",headers=HEADERS)
    assert accepted.status_code==200
    assert rejected.status_code==409 and rejected.json()["detail"]=="SEQUENCE_REPLAY"
    assert await real_count("AGNI-02")==after_first
    assert any(item["event_type"]=="SEQUENCE_REPLAY" and item["node_id"]=="AGNI-02" for item in events.json())
    assert secret not in accepted.text and secret not in rejected.text and secret not in events.text and secret not in caplog.text
