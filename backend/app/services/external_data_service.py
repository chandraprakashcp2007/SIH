"""
Provider-neutral external environmental-data architecture.

IMPORTANT:
Nothing is reported CONNECTED unless an adapter has actually completed a
verified retrieval and explicitly updates the provider state.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.external_data import (
    ExternalObservation,
    ExternalProviderState,
)


class ProviderState(str, Enum):
    CONNECTED = "CONNECTED"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    MANUAL_IMPORT = "MANUAL_IMPORT"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    PLANNED = "PLANNED"


PROVIDER_REGISTRY: dict[str, dict[str, Any]] = {
    "MOSDAC": {
        "display_name": "MOSDAC - SAC/ISRO",
        "capabilities": [
            "precipitation",
            "satellite_meteorology",
            "fire_smoke_context",
            "ocean_products",
        ],
        "default_state": ProviderState.NOT_CONFIGURED,
    },
    "IMD": {
        "display_name": "India Meteorological Department",
        "capabilities": [
            "rainfall",
            "temperature",
            "pressure",
            "wind",
            "severe_weather_context",
        ],
        "default_state": ProviderState.NOT_CONFIGURED,
    },
    "CWC": {
        "display_name": "Central Water Commission",
        "capabilities": [
            "river_level",
            "discharge",
            "flood_context",
        ],
        "default_state": ProviderState.NOT_CONFIGURED,
    },
    "INDIA_WRIS": {
        "display_name": "India-WRIS",
        "capabilities": [
            "hydrology",
            "river_context",
            "water_resources",
        ],
        "default_state": ProviderState.NOT_CONFIGURED,
    },
    "BHUVAN": {
        "display_name": "ISRO / NRSC Bhuvan",
        "capabilities": [
            "earth_observation",
            "disaster_layers",
            "dem",
            "flood_context",
        ],
        "default_state": ProviderState.NOT_CONFIGURED,
    },
    "GSI": {
        "display_name": "GSI Bhusanket / Bhukosh",
        "capabilities": [
            "landslide_inventory",
            "landslide_susceptibility",
            "geological_context",
        ],
        "default_state": ProviderState.NOT_CONFIGURED,
    },
    "NASA_FIRMS": {
        "display_name": "NASA FIRMS",
        "capabilities": [
            "active_fire",
            "historical_fire_hotspots",
        ],
        "default_state": ProviderState.NOT_CONFIGURED,
    },
    "FSI": {
        "display_name": "Forest Survey of India",
        "capabilities": [
            "forest_fire_context",
            "historical_fire_context",
        ],
        "default_state": ProviderState.NOT_CONFIGURED,
    },
    "INCOIS": {
        "display_name": "INCOIS",
        "capabilities": [
            "ocean",
            "waves",
            "sea_surface_temperature",
            "coastal_context",
        ],
        "default_state": ProviderState.NOT_CONFIGURED,
    },
}


class ExternalDataService:

    async def provider_statuses(
        self,
        db: AsyncSession,
    ) -> list[dict[str, Any]]:

        existing_result = await db.execute(
            select(ExternalProviderState)
        )

        existing = {
            row.provider: row
            for row in existing_result.scalars().all()
        }

        output = []

        for provider, definition in PROVIDER_REGISTRY.items():

            persisted = existing.get(provider)

            state = (
                persisted.state
                if persisted
                else definition["default_state"].value
            )

            output.append(
                {
                    "provider": provider,
                    "display_name": definition["display_name"],
                    "state": state,
                    "capabilities": definition["capabilities"],
                    "last_attempt_at": (
                        persisted.last_attempt_at if persisted else None
                    ),
                    "last_success_at": (
                        persisted.last_success_at if persisted else None
                    ),
                    "access_note": (
                        persisted.access_note if persisted else None
                    ),
                    "last_error": (
                        persisted.last_error if persisted else None
                    ),
                }
            )

        return output

    async def update_provider_state(
        self,
        db: AsyncSession,
        provider: str,
        state: ProviderState,
        *,
        access_note: str | None = None,
        error: str | None = None,
        successful: bool = False,
    ) -> ExternalProviderState:

        if provider not in PROVIDER_REGISTRY:
            raise ValueError(f"Unknown external provider: {provider}")

        item = await db.get(ExternalProviderState, provider)

        now = datetime.now(timezone.utc)

        if item is None:
            item = ExternalProviderState(provider=provider)
            db.add(item)

        item.state = state.value
        item.last_attempt_at = now
        item.access_note = access_note
        item.last_error = error

        if successful:
            item.last_success_at = now

        await db.flush()
        return item

    async def record_observation(
        self,
        db: AsyncSession,
        *,
        provider: str,
        dataset: str,
        product: str | None,
        observation_time: datetime,
        parameter: str,
        raw_value: Any,
        normalized_value: float | None = None,
        unit: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        region: str | None = None,
        freshness_seconds: int | None = None,
        quality_flags: list | None = None,
        source_identifier: str | None = None,
        source_url: str | None = None,
        access_note: str | None = None,
        checksum: str | None = None,
    ) -> ExternalObservation:

        if provider not in PROVIDER_REGISTRY:
            raise ValueError(f"Unknown external provider: {provider}")

        if observation_time.tzinfo is None:
            observation_time = observation_time.replace(
                tzinfo=timezone.utc
            )

        observation = ExternalObservation(
            provider=provider,
            dataset=dataset,
            product=product,
            retrieved_at=datetime.now(timezone.utc),
            observation_time=observation_time,
            latitude=latitude,
            longitude=longitude,
            region=region,
            parameter=parameter,
            raw_value=raw_value,
            normalized_value=normalized_value,
            unit=unit,
            freshness_seconds=freshness_seconds,
            quality_flags=quality_flags or [],
            source_identifier=source_identifier,
            source_url=source_url,
            access_note=access_note,
            checksum=checksum,
            provenance="EXTERNAL_DATA",
        )

        db.add(observation)
        await db.flush()

        return observation

    async def recent_observations(
        self,
        db: AsyncSession,
        *,
        provider: str | None = None,
        parameter: str | None = None,
        limit: int = 100,
    ) -> list[ExternalObservation]:

        query = select(ExternalObservation)

        if provider:
            query = query.where(
                ExternalObservation.provider == provider
            )

        if parameter:
            query = query.where(
                ExternalObservation.parameter == parameter
            )

        query = (
            query
            .order_by(desc(ExternalObservation.observation_time))
            .limit(min(max(limit, 1), 500))
        )

        result = await db.execute(query)
        return list(result.scalars().all())


external_data_service = ExternalDataService()
