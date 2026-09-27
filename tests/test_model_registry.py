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
async def test_dataset_manifest_validation_is_persisted_and_truthful():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        invalid=await client.post("/api/ml/datasets",headers=HEADERS,json={"name":"dem-placeholder","provenance":"EXTERNAL_DATA"})
        records=await client.get("/api/ml/datasets",headers=HEADERS)
    assert invalid.status_code==200
    assert invalid.json()["validation_status"]=="INVALID"
    assert "checksum" in invalid.json()["validation_errors"]
    assert any(item["id"]==invalid.json()["id"] for item in records.json())

@pytest.mark.asyncio
async def test_unvalidated_model_abstains_and_cites_validation_state():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        model=await client.post("/api/ml/models",headers=HEADERS,json={"name":"flood-forecast","version":"0.1","artifact_checksum":"abc123","provenance":"MODEL"})
        decision=await client.post(f"/api/ml/models/{model.json()['id']}/evaluate",headers=HEADERS,json={"features":{"water_level_cm":42}})
    assert model.json()["validation_status"]=="UNVALIDATED"
    assert decision.json()["decision"]=="ABSTAIN"
    assert decision.json()["reason"]=="MODEL_NOT_VALIDATED"
    assert decision.json()["model_id"]==model.json()["id"]

@pytest.mark.asyncio
async def test_drift_or_out_of_distribution_forces_abstention():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        model=await client.post("/api/ml/models",headers=HEADERS,json={"name":"test-validated-model","version":"1","artifact_checksum":"def456","provenance":"MODEL","validation_status":"VALIDATED","validation_evidence":{"dataset_id":"fixture","metrics":{"f1":0.9}}})
        drift=await client.post(f"/api/ml/models/{model.json()['id']}/drift",headers=HEADERS,json={"score":0.9,"threshold":0.2,"sample_count":20})
        decision=await client.post(f"/api/ml/models/{model.json()['id']}/evaluate",headers=HEADERS,json={"features":{"x":999}})
    assert drift.json()["state"]=="OUT_OF_DISTRIBUTION"
    assert decision.json()["decision"]=="ABSTAIN"
    assert decision.json()["reason"]=="OUT_OF_DISTRIBUTION"
