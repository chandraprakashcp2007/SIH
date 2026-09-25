# PRAHARI-NET Evidence Platform Design

## Intent

Extend the existing SIH26178 system into a truthful, evidence-gated environmental intelligence platform while preserving the working JALA, AGNI, BHUMI, VAYU, AKASHA, provenance, immediate-risk, alert, Copilot, map, report, WebSocket, simulator, and USB-serial flows. The central invariant is that immediate safety detection remains available without internet, terrain, external data, or ML, while forecasting publishes only when its hazard-specific evidence policy passes.

## Non-negotiable boundaries

- `data/prahari.db` is a preserved recovery case and is never modified by tests or repaired in place.
- Tests select an isolated database before importing application modules.
- `REAL`, `SIMULATION`, `EXTERNAL_DATA`, `REPLAY`, and `PLANNED` remain distinct provenance modes.
- External observations cannot enter the physical telemetry tables as `REAL`.
- Provider state is derived from configuration and verified retrievals; it is never optimistically marked `CONNECTED`.
- Immediate detection and alerting do not depend on forecast services.
- Simulator records cannot qualify a historical model as trained on real evidence.
- Models that are untrained, unvalidated, out of distribution, or insufficiently confident abstain.
- Generated databases, SQLite sidecars, reports, downloaded datasets, secrets, and temporary model artifacts are excluded from Git.

## Architecture

The existing FastAPI application remains the composition root. Focused SQLAlchemy model modules and services add external observations, datasets, terrain, models, predictions, evidence, continuity, outbound delivery, and event memory. API routers expose paginated read models and protected mutation/import operations. Existing telemetry ingestion continues to call the immediate risk and alert pipeline directly; prediction evaluation is a separate downstream operation that cannot block local safety behavior.

The React application keeps its current navigation shell, visual tokens, lazy routes, authenticated API client, and WebSocket service. New pages consume truthful backend states and share compact status/evidence components. Missing data is rendered as missing, unavailable, withheld, or planned rather than as zero-valued evidence.

## Data and provenance

External provider adapters normalize legitimate API or manually imported observations into `ExternalObservation`, preserving provider, dataset, product, observation/retrieval timestamps, coordinates, parameter, raw and normalized values, units, freshness, quality flags, source metadata, checksum, and `EXTERNAL_DATA` provenance. A registry reports one of `CONNECTED`, `DEGRADED`, `OFFLINE`, `AUTH_REQUIRED`, `MANUAL_IMPORT`, `NOT_CONFIGURED`, or `PLANNED`.

Dataset manifests, installations, processing runs, and quality results track source coverage, variables, units, record counts, checksums, preprocessing versions, and validation failures. Imports are allow-listed data formats, size bounded, stored below `data/raw`, checksum verified, and never executable.

Terrain processing accepts genuine GeoTIFF rasters. Raster loading is lazy; elevation, slope, aspect, local relief, and justified derivatives carry raster checksum, resolution, CRS, processing version, and calculation time. Missing DEM produces unavailable evidence, never synthetic terrain.

Training consumes only installed, quality-passing dataset manifests. Time/geography-aware splits feed CPU-friendly interpretable estimators. Evaluation metrics are calculated from held-out samples and stored with limitations. Artifact checksums and dataset dependencies are registered; no artifact or metric is fabricated.

## Detection and prediction

Path A remains: physical/simulated packet -> validation -> sensor trust -> local risk logic -> alert. Path B is: validated evidence -> temporal persistence -> heterogeneous corroboration -> optional terrain/external/history/model evidence -> uncertainty and robustness -> prediction gate.

Predictions move through `COLLECTING`, `VALIDATING`, `CORROBORATING`, `READY`, `WITHHELD`, and `PUBLISHED`. Hazard policies distinguish required from optional tests. Failed required tests produce first-class withholding reasons and evidence-deficit actions. Publishing requires an eligible model where a policy requires model evidence, sufficient decision integrity, and no provenance violation.

Consensus records agreeing and conflicting heterogeneous evidence. Counterfactual robustness removes the weakest available source and reruns the deterministic gate, producing `ROBUST`, `MODERATELY_ROBUST`, or `FRAGILE`; it is not presented as causal proof. Contribution analysis reports only deterministic implemented contributions.

## Cross-hazard, memory, and continuity

A declarative Pancha Bhootha graph requests secondary-risk reevaluation without claiming deterministic causation. Site baselines and event fingerprints use actual stored history and retain progression, peak, recovery, sensor trust, network state, model version, terrain, and external evidence.

The continuity service derives `FULL_ONLINE`, `LOCAL_WIFI`, `LOCAL_EDGE`, `NODE_ONLY`, `STORE_FORWARD`, `RECOVERING`, or `EXTERNAL_DATA_DEGRADED`. A durable, checksum-addressed outbound queue provides idempotent acknowledgement and reconnect synchronization. Transport capability truthfully distinguishes `LIVE`, `SUPPORTED`, `PLANNED`, and `UNAVAILABLE`. Cached data is never labeled live.

## Interfaces and security

New routers cover external data, datasets, terrain, models, predictions/evidence, continuity, interoperability export, and compliance. Read endpoints use existing authentication. Provider retrieval, dataset import, simulator/demo mutations, and synchronization controls require appropriate gateway/admin authorization. Secrets stay server-side; production rejects silent development bypass and insecure default secrets.

CAP output is labeled “CAP-compatible interoperability export” and schema validated; no official NDMA/SACHET integration is claimed. Copilot remains read-only and answers evidence questions only from persisted project state.

## Delivery and verification

Fourteen vertical slices follow the approved order. Each behavioral slice uses red-green-refactor tests, then runs backend regression, frontend tests, type checking/build, and relevant desktop/mobile Playwright checks before a stable commit. The final audit searches unsupported claims, runs the readiness script from real command results, produces an evidence-linked completion matrix, and pushes only a green `main`.

