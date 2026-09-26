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


@pytest.mark.asyncio
async def test_cross_hazard_reevaluation_uses_configured_relationship_language():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/cascades/reevaluate", headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["relationships"]
    assert all(item["relationship_type"] == "CONFIGURED_RELATIONSHIP" for item in body["relationships"])
    assert all("causal" not in item["explanation"].lower() for item in body["relationships"])
    assert all(item["provenance"] in {"REAL", "SIMULATION", "EXTERNAL_DATA", "MODEL"} for item in body["relationships"])


@pytest.mark.asyncio
async def test_compound_risk_is_rule_based_and_consensus_reports_missing_neighbours():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/cascades/reevaluate", headers=AUTH_HEADERS)
        consensus = await client.get("/api/consensus", headers=AUTH_HEADERS)
    assert response.status_code == 200
    compounds = response.json()["compound_risks"]
    assert all(item["method"] == "TRANSPARENT_RULE" for item in compounds)
    assert all("sum" not in item["explanation"].lower() for item in compounds)
    assert consensus.status_code == 200
    assert all(item["state"] == "INSUFFICIENT_NEIGHBOURS" for item in consensus.json())
