from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.schemas.external_data import (
    ExternalObservationOut,
    ExternalProviderStatusOut,
)
from backend.app.services.external_data_service import (
    external_data_service,
)


router = APIRouter(
    prefix="/external",
    tags=["External Environmental Data"],
)


@router.get(
    "/status",
    response_model=list[ExternalProviderStatusOut],
)
async def external_provider_status(
    db: AsyncSession = Depends(get_db),
):
    """
    Return truthful provider states.

    Providers are NOT reported CONNECTED unless a verified adapter
    explicitly recorded a successful connection.
    """
    return await external_data_service.provider_statuses(db)


@router.get(
    "/observations",
    response_model=list[ExternalObservationOut],
)
async def external_observations(
    provider: str | None = None,
    parameter: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Return stored external observations only.

    These observations always retain EXTERNAL_DATA provenance and are
    never converted into physical node telemetry.
    """
    return await external_data_service.recent_observations(
        db,
        provider=provider,
        parameter=parameter,
        limit=limit,
    )
