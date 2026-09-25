# PRAHARI-NET Evidence Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the approved evidence-gated, dataset-backed, terrain-aware, offline-resilient PRAHARI-NET software specification without weakening the existing safety system.

**Architecture:** Preserve the current FastAPI/SQLAlchemy and React/Vite composition, add focused domain services and persistence per vertical slice, and keep immediate detection independent from forecasting. All externally sourced, modeled, cached, simulated, and planned states remain explicitly distinguishable.

**Tech Stack:** Python 3, FastAPI, SQLAlchemy async, Pydantic, SQLite/PostgreSQL, scikit-learn, rasterio/numpy where available, React 19, TypeScript, Vite, Vitest, Playwright.

**Spec:** `docs/superpowers/specs/2026-09-25-prahari-evidence-platform-design.md`

## Global Constraints

- Preserve `data/prahari.db`; tests must never open it.
- Preserve the five provenance modes and all existing immediate safety behavior.
- Never fabricate observations, provider connections, terrain, metrics, model validation, hardware, transports, or integrations.
- Use protected, bounded, allow-listed import and mutation endpoints.
- Use test-first behavior changes and commit only green stable slices.
- Baseline: backend 81, frontend 6, Playwright 4, typecheck and build passing with an isolated DB.

## Review Focus

- A test process with a populated `.env` must still select an isolated database before application import.
- Duplicate imports, telemetry, and reconnect deliveries must be idempotent without duplicate incidents.
- Naive/future/stale timestamps and invalid coordinates or units must fail deterministically.
- Missing optional evidence may reduce confidence, but missing required evidence must withhold publication.
- Restarting the backend must preserve queue, prediction, dataset, and provenance state.

---

### Task 1: Repository hygiene, isolated tests, and README structure

**Files:** Create `tests/conftest.py`; modify `.gitignore`, `README.md`, `scripts/run-tests.ps1`; remove tracked generated artifacts.

**Interfaces:** Produces an isolated test `DATABASE_URL` set before backend imports and a verification script that propagates real exit status.

- [ ] Add a subprocess regression test proving pytest does not resolve `settings.DATABASE_URL` to `data/prahari.db`.
- [ ] Run it and confirm failure against the current suite.
- [ ] Set a per-run test database in root `tests/conftest.py`, initialize it through existing seed functions, and clean it after disposal.
- [ ] Ignore/untrack `*.db-wal`, `*.db-shm`, test databases, `playwright-report/`, and `test-results/` without touching `data/prahari.db`.
- [ ] Move BHUMI sensor/metric bullets under BHUMI and preserve VAYU/AKASHA truth labels.
- [ ] Run backend, frontend, typecheck/build, and Playwright; commit Slice 1.

### Task 2: External observations and provider registry

**Files:** Create `backend/app/models/external_data.py`, `backend/app/services/external_data/{base,registry,service,providers}.py`, `backend/app/api/external_data.py`; modify model exports, initialization, and `main.py`; test `tests/test_external_data.py`.

**Interfaces:** Produce `ExternalDataAdapter.status()`, `fetch()`, `import_observations()`, `ProviderRegistry`, and normalized `ExternalObservation` persistence with forced `EXTERNAL_DATA` provenance.

- [ ] Write failing tests for all provider defaults, normalized fields, retry/backoff/cache metadata, and rejection of `REAL` provenance.
- [ ] Implement adapters for MOSDAC, IMD, CWC, INDIA-WRIS, Bhuvan, GSI, FIRMS, FSI, and INCOIS using configuration/manual import truth states.
- [ ] Add authenticated list/detail/observation APIs and verify no adapter reports unverified `CONNECTED`.
- [ ] Run regression gates and commit Slice 2.

### Task 3: Dataset manager and quality pipeline

**Files:** Create `backend/app/models/datasets.py`, `backend/app/services/dataset_manager.py`, `backend/app/services/data_quality.py`, `backend/app/api/datasets.py`, data directory placeholders; test `tests/test_datasets.py`.

**Interfaces:** Produce manifest/install/run/quality records plus bounded `CSV`, `JSON`, `GeoJSON`, `Parquet`, `GeoTIFF`, `NetCDF`, and `HDF/HDF5` import dispatch.

- [ ] Write failing tests for checksum mismatch, corruption, schema drift, duplicates, invalid coordinates/units/physics, gaps, outliers, and path/format rejection.
- [ ] Implement streaming checksum, safe filenames, size limits, atomic installation, manifest persistence, and quality summaries.
- [ ] Protect imports with admin authorization and expose paginated read APIs.
- [ ] Run regression gates and commit Slice 3.

### Task 4: Terrain intelligence

**Files:** Create `backend/app/models/terrain.py`, `backend/app/services/terrain_service.py`, `backend/app/api/terrain.py`; test `tests/test_terrain.py` with a small generated GeoTIFF fixture.

**Interfaces:** Produce safe raster registration and point/window calculations with provenance; return unavailable when no valid raster covers a point.

- [ ] Write failing tests for missing DEM, checksum/projection metadata, elevation, slope, aspect, relief, out-of-bounds points, and malformed raster rejection.
- [ ] Add optional geospatial dependencies and lazy raster loading with bounded windows.
- [ ] Persist raster/source and derived-feature provenance; never infer hazard from DEM alone.
- [ ] Run regression gates and commit Slice 4.

### Task 5: Historical training, evaluation, and model registry

**Files:** Create `backend/app/models/model_registry.py`, `backend/app/services/model_registry.py`, `training/`, `preprocessing/`, `evaluation/`, `backend/app/api/models.py`; test `tests/test_model_registry.py` and `tests/test_training_pipeline.py`.

**Interfaces:** Produce manifest-driven time/geography splits, computed metrics, checksummed artifacts, eligibility/abstention decisions, and model status APIs.

- [ ] Write failing tests preventing simulator/replay training, random-row leakage, hardcoded metrics, unvalidated inference, and OOD publication.
- [ ] Implement CPU-friendly estimators, calibration evaluation, artifact metadata, limitations, and `UNTRAINED` through `RETIRED` lifecycle.
- [ ] Expose read-only model/evaluation APIs and protected training registration.
- [ ] Run regression gates and commit Slice 5.

### Task 6: Detection/prediction separation and evidence gate

**Files:** Create focused prediction/evidence models and `backend/app/services/evidence_gate.py`, `prediction_service.py`; extend prediction APIs and evidence capsules; test `tests/test_prediction_gate.py`.

**Interfaces:** Produce hazard policies, evidence results, distinct risk/confidence/decision-integrity values, and valid state transitions through publication.

- [ ] Write failing tests showing Path A alerts work while internet, terrain, model, and external services are unavailable.
- [ ] Write failing tests for each prediction state, illegal transitions, provenance isolation, trust/persistence requirements, and publish authorization.
- [ ] Implement deterministic policy evaluation and persistence without changing the immediate alert call path.
- [ ] Run regression gates and commit Slice 6.

### Task 7: Withholding, deficits, consensus, and robustness

**Files:** Create `backend/app/services/evidence_deficit.py`, `consensus_service.py`, `robustness_service.py`; extend prediction schemas/APIs; test `tests/test_prediction_decisions.py`.

**Interfaces:** Produce explicit withholding reasons/actions, heterogeneous consensus, weakest-source counterfactual reruns, and deterministic contributions.

- [ ] Write failing tests for every withholding reason, contradictory evidence, fragile decisions, and missing-evidence actions.
- [ ] Implement the services and expose “why withheld” detail without invented SHAP values.
- [ ] Run regression gates and commit Slice 7.

### Task 8: Cross-hazard intelligence and environmental memory

**Files:** Create cross-hazard, baseline, event-fingerprint models/services and APIs; test `tests/test_cross_hazard.py`.

**Interfaces:** Produce declarative secondary reevaluation requests, site-local baselines, event fingerprints, and expanded evidence capsules.

- [ ] Write failing tests for rain/flood/landslide, fire/air, heat/fire, severe-weather, and industrial-gas relationships plus provenance-preserving baselines.
- [ ] Implement graph traversal with cycle/duplicate protection and persist actual-history fingerprints.
- [ ] Run regression gates and commit Slice 8.

### Task 9: Continuity and store-carry-forward

**Files:** Create continuity and outbound-queue models/services/APIs; extend WebSocket synchronization and frontend cache service; test backend continuity and frontend reconnect behavior.

**Interfaces:** Produce derived network modes, checksum-idempotent queue states, replay-safe acknowledgements, last-event synchronization, and polling fallback.

- [ ] Write failing tests for internet/gateway loss, local operation, queue retries, restart persistence, duplicate acknowledgement, reconnect sync, and cached/stale labeling.
- [ ] Implement persisted queue transitions and event cursor synchronization.
- [ ] Run regression gates and commit Slice 9.

### Task 10: Transport abstraction and CAP-compatible export

**Files:** Create `backend/app/transports/`, CAP schema/service/API, and tests.

**Interfaces:** Preserve USB serial as live where configured; represent WIFI/LORA/LORAWAN/NB_IOT/CELLULAR/5G capability states; produce validated CAP-compatible XML/JSON.

- [ ] Write failing contract tests for transport truth states and required CAP fields.
- [ ] Adapt the serial gateway behind the interface without fabricating radio packets or official integration.
- [ ] Run regression gates and commit Slice 10.

### Task 11: Operational UI pages

**Files:** Add shared evidence/status components and the nine approved pages; modify `App.tsx`, `Sidebar.tsx`, API types/client, map overlays; add Vitest and Playwright coverage.

**Interfaces:** Consume backend read models for fusion, providers, datasets, terrain, predictions/detail, models, continuity, compliance, and costs.

- [ ] Write failing component tests for truthful missing/planned/withheld states and provenance labels.
- [ ] Implement lazy routes in the current design system, mobile layouts, safe dataset import, and evidence-derived compliance.
- [ ] Add desktop/mobile navigation and detail-flow Playwright tests.
- [ ] Run regression gates and commit Slice 11.

### Task 12: Copilot, judge demo, and readiness

**Files:** Extend read-only Copilot tools/intents, demo service/page, `scripts/run-readiness.ps1`, and associated tests.

**Interfaces:** Answer evidence/model/terrain/provenance/continuity questions from stored state and produce real `PASS/WARN/FAIL` readiness results from command exit codes.

- [ ] Write failing safety tests proving Copilot and demo controls cannot mutate risk/trust or bypass publication gates.
- [ ] Implement supported, withheld, and offline demo scenarios with explicit simulation labels and idempotent recovery.
- [ ] Add the requested readiness cases and real command aggregation.
- [ ] Run regression gates and commit Slice 12.

### Task 13: Security, documentation, and claims audit

**Files:** Harden config/auth/import controls; update README and all requested `docs/*.md`; add security tests and audit script/output.

**Interfaces:** Production startup validation rejects insecure defaults/bypass; documentation links proof and external blockers.

- [ ] Write failing tests for protected mutations, secret exposure, production bypass/default keys, CORS, unsafe filenames, and oversize imports.
- [ ] Implement minimal hardening and document deployment, architecture, datasets, terrain, models, predictions, continuity, demo, and SIH matrix.
- [ ] Search and correct unsupported deployment/accuracy/integration claims.
- [ ] Run regression gates and commit Slice 13.

### Task 14: Final verification, evidence matrix, and delivery

**Files:** Update final readiness/audit report and completion matrix from executed evidence only.

**Interfaces:** Produce exact command results, capability states, blockers, commit SHA, and judge procedure.

- [ ] Run isolated backend tests, frontend unit tests, standalone typecheck, production build, desktop/mobile Playwright, readiness, security/claim audits, and database-restart checks.
- [ ] Verify Git excludes runtime/download/model artifacts and the working tree contains only intentional changes.
- [ ] Commit the final evidence report, push green `main` to `origin`, and report the pushed SHA and evidence-based completion matrix.

