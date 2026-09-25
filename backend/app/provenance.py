from enum import Enum


class SourceMode(str, Enum):
    REAL = "REAL"
    SIMULATION = "SIMULATION"
    EXTERNAL_DATA = "EXTERNAL_DATA"
    REPLAY = "REPLAY"
    PLANNED = "PLANNED"


class ValidationReason(str, Enum):
    INVALID_SCHEMA = "INVALID_SCHEMA"
    DUPLICATE = "DUPLICATE"
    STALE_PACKET = "STALE_PACKET"
    FUTURE_TIMESTAMP = "FUTURE_TIMESTAMP"
    OUT_OF_ORDER = "OUT_OF_ORDER"
    INVALID_SOURCE_MODE = "INVALID_SOURCE_MODE"
    PLANNED_NODE_TELEMETRY = "PLANNED_NODE_TELEMETRY"
    PROVENANCE_CONFLICT = "PROVENANCE_CONFLICT"
    PHYSICAL_RANGE_FAILURE = "PHYSICAL_RANGE_FAILURE"


def resolve_source_mode(source_mode: SourceMode | str | None, is_simulation: bool | None) -> SourceMode:
    if source_mode is not None:
        return source_mode if isinstance(source_mode, SourceMode) else SourceMode(source_mode)
    return SourceMode.SIMULATION if is_simulation else SourceMode.REAL
