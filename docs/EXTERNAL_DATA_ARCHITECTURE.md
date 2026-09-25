# PRAHARI-NET External Data Architecture

## Purpose

PRAHARI-NET separates physical node telemetry from authoritative external
environmental observations.

External observations use the provenance value:

`EXTERNAL_DATA`

They are never silently converted into `REAL` physical telemetry.

## Provider Registry

The platform has provider definitions for:

- MOSDAC
- IMD
- CWC
- India-WRIS
- ISRO/NRSC Bhuvan
- GSI
- NASA FIRMS
- Forest Survey of India
- INCOIS

Provider registration does **not** mean a provider is live.

A provider remains `NOT_CONFIGURED`, `AUTH_REQUIRED`,
`MANUAL_IMPORT`, `OFFLINE`, `DEGRADED`, or `PLANNED`
until the corresponding adapter/import workflow establishes otherwise.

`CONNECTED` may only be recorded after an actual successful retrieval.

## Stored Observation Provenance

Every observation may store:

- provider
- dataset
- product
- retrieval time
- observation time
- location
- parameter
- raw value
- normalized value
- unit
- freshness
- quality flags
- source identifier
- source URL
- access note
- checksum
- provenance

## Safety Boundary

External provider failure must never disable PRAHARI's immediate
local physical-sensor safety path.

External observations may later contribute to evidence-gated prediction,
but missing external evidence must be represented honestly rather than
fabricated.
