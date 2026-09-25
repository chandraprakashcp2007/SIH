from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from backend.app.core.database import AsyncSessionLocal
from backend.app.core.security import create_access_token
from backend.app.main import app
from backend.app.models.external_data import ExternalObservation
from backend.app.services.external_data_service import (
    PROVIDER_REGISTRY,
    ProviderState,
    external_data_service,
)


AUTH_HEADERS = {
    "Authorization": (
        "Bearer "
        + create_access_token(
            {
                "sub": "admin",
                "role": "ADMIN",
                "dev_auth_bypass": True,
            }
        )
    )
}


@pytest.mark.asyncio
async def test_provider_registry_contains_required_authoritative_sources():

    expected = {
        "MOSDAC",
        "IMD",
        "CWC",
        "INDIA_WRIS",
        "BHUVAN",
        "GSI",
        "NASA_FIRMS",
        "FSI",
        "INCOIS",
    }

    assert set(PROVIDER_REGISTRY) == expected


@pytest.mark.asyncio
async def test_external_status_never_fabricates_connected_provider():

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:

        response = await client.get(
            "/api/external/status",
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200

    items = response.json()

    assert len(items) == 9

    for item in items:
        assert item["state"] != ProviderState.CONNECTED.value


@pytest.mark.asyncio
async def test_external_observation_is_forced_to_external_data_provenance():

    async with AsyncSessionLocal() as db:

        observation = await external_data_service.record_observation(
            db,
            provider="NASA_FIRMS",
            dataset="TEST_FIXTURE_ONLY",
            product="UNIT_TEST",
            observation_time=datetime.now(timezone.utc),
            parameter="active_fire_test",
            raw_value={"fixture": True},
            normalized_value=1.0,
            unit="test",
            quality_flags=["TEST_ONLY"],
            source_identifier="pytest",
            access_note="Automated isolated test fixture",
        )

        await db.commit()

        stored = await db.get(
            ExternalObservation,
            observation.id,
        )

        assert stored is not None
        assert stored.provenance == "EXTERNAL_DATA"


@pytest.mark.asyncio
async def test_external_observation_does_not_become_node_telemetry():

    async with AsyncSessionLocal() as db:

        observations = (
            await db.execute(
                select(ExternalObservation)
            )
        ).scalars().all()

        for observation in observations:
            assert observation.provenance == "EXTERNAL_DATA"


@pytest.mark.asyncio
async def test_unknown_provider_is_rejected():

    async with AsyncSessionLocal() as db:

        with pytest.raises(ValueError):

            await external_data_service.record_observation(
                db,
                provider="FAKE_PROVIDER",
                dataset="invalid",
                product=None,
                observation_time=datetime.now(timezone.utc),
                parameter="invalid",
                raw_value={"invalid": True},
            )
