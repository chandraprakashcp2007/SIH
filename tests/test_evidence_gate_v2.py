import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.main import app


AUTH_HEADERS = {"Authorization": f"Bearer {create_access_token({'sub': 'admin', 'role': 'ADMIN', 'dev_auth_bypass': True})}"}


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    asyncio.run(seed_data())


def evidence(provenance="REAL"):
    return [{
        "hazard": "FLOOD", "source": "JALA-01:water_level_cm",
        "provider": "PRAHARI-NET", "provenance": provenance,
        "freshness_seconds": 5, "quality": 0.95, "trust": 0.92,
        "spatial_relevance": 1.0, "temporal_relevance": 1.0,
        "claim": {"property": "water_level_cm", "value": 180, "unit": "cm"},
        "metadata": {"packet_valid": True, "physically_plausible": True,
                     "persistent": True, "momentum": True,
                     "multi_sensor_agreement": True, "regional_consensus": True},
    }]


@pytest.mark.asyncio
async def test_gate_withholds_when_required_authoritative_and_model_checks_unavailable():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/evidence-gate/evaluate", headers=AUTH_HEADERS, json={
            "hazard": "FLOOD", "severity": "CRITICAL", "operational_provenance": "REAL",
            "evidence": evidence(),
        })
    assert response.status_code == 200
    body = response.json()
    assert body["lifecycle"] == "WITHHELD"
    assert body["publication_allowed"] is False
    by_check = {item["number"]: item for item in body["checks"]}
    assert by_check[10]["status"] == "UNAVAILABLE"
    assert by_check[12]["status"] == "UNAVAILABLE"
    assert by_check[10]["required"] is True
    assert body["why_withheld"]


@pytest.mark.asyncio
async def test_simulation_evidence_cannot_strengthen_real_gate():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/evidence-gate/evaluate", headers=AUTH_HEADERS, json={
            "hazard": "FLOOD", "severity": "WATCH", "operational_provenance": "REAL",
            "evidence": evidence("SIMULATION"),
        })
    body = response.json()
    provenance_check = next(item for item in body["checks"] if item["number"] == 2)
    assert provenance_check["status"] == "FAILED"
    assert body["publication_allowed"] is False
