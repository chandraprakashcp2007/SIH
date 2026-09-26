# PRAHARI-NET V2 Master Plan

Date: 2026-09-27  
System: Predictive Resilient Autonomous Hazard & Risk Intelligence Network  
Architecture identity: Pancha-Bhootha Environmental Intelligence Fabric

## 1. Phase 0 repository audit

### Existing architecture

PRAHARI-NET is a single-repository FastAPI/SQLAlchemy backend and React/Vite PWA. Telemetry enters through HTTP, the Python USB-serial gateway, or the in-process simulator; all three converge on `TelemetryService`. The backend persists telemetry, risk, trust, alerts, network packet logs, audit logs, Copilot sessions, and external-data metadata in async SQLAlchemy. `/ws/live` publishes incremental telemetry and risk events. The frontend uses authenticated REST calls, a WebSocket client, Leaflet, route-level lazy loading, and service-worker caching.

The authoritative immediate path is:

`packet -> provenance/timestamp/sequence validation -> history -> trust/risk engine -> telemetry/risk/trust/network persistence -> alert evaluation -> WebSocket`

Replay is stored without updating operational state. Simulation cannot replace a node already marked REAL. External observations have separate persistence and cannot enter telemetry as REAL.

### Verified baseline

| Gate | Result | Evidence |
|---|---|---|
| Git state | Clean `main` at `dabb7838` before this program | `git status --short`, `git log` |
| Backend tests, default environment | 70 passed, 9 failed, 19 errors | Live `data/prahari.db` is malformed and tests were coupled to it |
| Backend tests, isolated database | 98 passed | `DATABASE_URL=sqlite+aiosqlite:///./data/prahari_baseline_isolated.db pytest -q -p no:cacheprovider` |
| Frontend unit tests | 9 passed in 6 files | `npm test -- --run` outside restricted process sandbox |
| Frontend production build | Passed, 1912 modules | `npm run build` |
| Playwright | BLOCKED before cases ran | Existing process occupies `127.0.0.1:5173`; configuration forbids reuse |

The operational database and sidecars are preserved. No repair, deletion, or replacement is authorized by this plan.

### Feature inventory summary

Implemented: authenticated telemetry ingestion, provenance modes, replay isolation, five domain registry entries, deterministic simulator, USB serial bridge, risk/trust engine, alert lifecycle, WebSocket stream, historical node telemetry, external-provider registry foundation, Copilot read tools, readiness/calibration/report pages, PWA cache, Docker production image.

Partial: canonical observations, geospatial intelligence, five domain experiences, evidence fusion/gating, sensor digital twin, aggregation windows, provider adapters, model lifecycle, CAP, offline mutation queue, incident reporting, assurance dashboards.

Stub or simulated: VAYU particulate measurements, AKASHA wind/weather, camera confidence, all demo hazards. These are acceptable only with SIMULATION provenance.

Not configured: authoritative external providers, DEM/terrain raster, satellite feeds, calibrated PM hardware, SMS/government delivery, LoRa validation, SIM800L, validated forecast artifacts.

Planned: dedicated map engines, cross-hazard/compound-risk persistence, upstream topology, time-to-impact, impact/evacuation, secure signed telemetry, black box, chaos/scenario isolation, recovery intelligence, full SensorThings/STAC/CAP interoperability.

### Material audit findings

1. Tests use the live database unless callers override `DATABASE_URL`; this caused the baseline corruption failures.
2. There is no Alembic or equivalent migration framework; startup uses additive `create_all` plus limited SQLite column patching.
3. There is no firmware source in the repository.
4. `docker-compose.yml` references `backend/Dockerfile` and `frontend/Dockerfile`, which are absent; the root production `Dockerfile` is the reproducible path currently evidenced.
5. The UI provides one map page and five-domain summaries, not five dedicated live intelligence maps.
6. No provider is proven live. Registry states must remain NOT_CONFIGURED, MANUAL_IMPORT, or PLANNED until verified retrieval succeeds.
7. Historical charts read persisted telemetry, but required 15m/1h/6h/24h/7d backend aggregation is incomplete.
8. Existing alert evidence is useful but is not the requested persisted 15-check, hazard-specific Evidence Gate.
9. Model/risk labels must not be described as scientifically validated; no qualifying model artifact/dataset validation evidence is present.

## 2. Target architecture

Preserve the current composition root and add bounded modules around it:

`Sources -> canonical Observation adapter -> provenance/quality/trust -> evidence store -> hazard policy gate -> predictions/cascades/compound risk -> incidents/alerts/CAP -> operational read models`

Immediate local detection remains independent of forecasting and external providers. Every derived record stores evidence references, provenance, algorithm/policy version, timestamps, confidence and uncertainty where meaningful. Frontend pages consume backend read models and show unavailable states rather than inventing values.

## 3. Database and migration strategy

Introduce a migration framework before schema expansion. The baseline migration must stamp existing databases without dropping tables and create new tables additively. SQLite remains supported for development; PostgreSQL is production. New high-volume tables use indexes on time, node, sensor, domain, incident, hazard and status. Geometry is initially GeoJSON plus bounding-box columns, with optional PostGIS acceleration behind a capability check.

Core additions by phase: observations and sensor metadata; geospatial datasets/features; health/fault/calibration records; evidence/gate policies/results; cascades/compound risks/consensus; topology/predictions/time-to-impact; twins/boundaries/uncertainty; assets/routes/shelters; CAP/delivery; continuity queues; security events/nonces/audit-chain; dataset/model registries; event memory; scenarios/chaos runs; recovery/damage/reports.

## 4. API and event strategy

Keep existing endpoints stable. Add version-compatible routers under the requested module names only where no equivalent exists. Collection routes require pagination, time filters and bounding boxes. Mutations use existing RBAC and audit logging.

Normalize new events to dot-separated names (`telemetry.received`, `sensor.health.changed`, `prediction.withheld`, and related types) while continuing to emit legacy event names until frontend migration is complete. WebSockets carry deltas, never complete history.

## 5. Delivery phases and gates

Each phase follows RED -> GREEN -> regression -> build -> relevant E2E -> documentation -> separate commit. A phase does not advance with unexplained regression.

| Phase | Deliverable | Acceptance gate |
|---|---|---|
| 0 | Forensics, isolated tests, master plan, feature matrix | 98 backend; 9 frontend; build; E2E blocker documented |
| 1 | Canonical Observation/provenance foundation and legacy adapter | Implemented: additive table creation, legacy adapter, payload hashing and read-only SensorThings subset; provenance regression passes |
| 2 | Dataset registry, GeoJSON engine, five distinct domain map read models/pages | Implemented: persisted registry/feature schema, backend-derived risk GeoJSON, five dedicated routes, truthful layer states and E2E coverage |
| 3 | Sensor health/trust history and server-side graph aggregation | Implemented: persisted health snapshots, fleet API/UI, health events and 15m–7d database aggregation |
| 4 | Evidence items, fusion, hazard policies, 15-check gate, decay | mandatory checks prevent publication |
| 5 | Cross-hazard, compound risk and regional consensus | no statistical-causality claims; isolation tests pass |
| 6 | JALA topology, downstream threat, predictions, time-to-impact | unavailable travel time stays unavailable |
| 7 | Digital twin, hazard/uncertainty boundaries and blind spots | confidence/uncertainty displayed separately |
| 8 | Impact, dependencies, evacuation and safe zones | routes never claim guaranteed safety |
| 9 | CAP 1.2 export, multilingual templates, delivery proof | XML schema/contract and delivery-state tests pass |
| 10 | Offline queue, continuity, adaptive network/energy policies | idempotent reconnect and stale labels pass |
| 11 | Signed telemetry, replay defense, security centre, audit chain | replay fixture rejected without REAL mutation |
| 12 | Dataset manager, model registry, drift/abstention | unvalidated/OOD models abstain |
| 13 | Disaster memory, fingerprints and immutable black-box replay | replay cannot write operational state |
| 14 | Isolated deterministic Scenario Lab and Chaos Lab | simulation cannot strengthen REAL |
| 15 | Recovery, damage evidence and evidence-backed reports | human verification and no auto all-clear |
| 16 | Copilot 2.0 grounded evidence explanations | no fabricated evidence/claims |
| 17 | SensorThings subset, GeoJSON, STAC metadata, assurance/DDQI | interoperability contract tests pass |
| 18 | Full regression, security, performance and E2E | all local acceptance gates pass |
| 19 | Production migration/deploy/smoke | requires deployment credentials/permission and hardware/provider evidence |

## 6. Rollback strategy

Every phase is a separate commit and additive migration. Rollback disables new routers/events through configuration first, then reverts the phase commit. Migrations never drop legacy columns or tables during this program; rollback migrations remove only newly created, demonstrably empty structures. Existing REST and WebSocket contracts remain available through compatibility adapters. Operational data is backed up and integrity-checked before any production migration.

## 7. External blockers

Authoritative datasets, provider credentials/licences, physical ESP32/sensors, LoRa/SIM800L validation, official alert-delivery authority, production database, Railway access, DNS/TLS and deployment permission are external dependencies. Their interfaces, tests and NOT_CONFIGURED states can be implemented locally; they cannot be truthfully marked connected or production-verified without those dependencies.
