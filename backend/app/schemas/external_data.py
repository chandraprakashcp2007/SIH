from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ExternalObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    provider: str
    dataset: str
    product: str | None

    retrieved_at: datetime
    observation_time: datetime

    latitude: float | None
    longitude: float | None
    region: str | None

    parameter: str
    raw_value: Any
    normalized_value: float | None
    unit: str | None

    freshness_seconds: int | None
    quality_flags: list

    source_identifier: str | None
    source_url: str | None
    access_note: str | None
    checksum: str | None

    provenance: str


class ExternalProviderStatusOut(BaseModel):
    provider: str
    display_name: str
    state: str
    capabilities: list[str]
    last_attempt_at: datetime | None = None
    last_success_at: datetime | None = None
    access_note: str | None = None
    last_error: str | None = None
