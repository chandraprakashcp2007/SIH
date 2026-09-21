# PRAHARI-NET Final Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden and complete the existing PRAHARI-NET system for a reliable, offline-first SIH demonstration.

**Architecture:** Preserve the current FastAPI/SQLite backend and React/Vite frontend. Strengthen existing boundaries in vertical slices, with telemetry ingestion and authenticated API contracts as the central interfaces.

**Tech Stack:** Python 3, FastAPI, SQLAlchemy async, SQLite, pytest, React 19, TypeScript, Vite, Leaflet, Vitest, Playwright.

**Spec:** `docs/superpowers/specs/2026-09-21-prahari-final-hardening-design.md`

## Global Constraints

- Preserve working modules and the single frontend/backend architecture.
- No internet dependency for local monitoring or local Copilot.
- Test-first for every behavior change.
- Never fabricate sensor or camera evidence.
- Do not delete, reset, or clean untracked project content.

## Review Focus

- Explicit invalid node identifiers must not be rewritten through aliases.
- Duplicate/out-of-order telemetry must not mutate operational state.
- Development bypass must never activate when disabled.
- Cached/offline data must be labeled and timestamped.
- Viewer, operator, and admin permissions must differ at mutation boundaries.

---

### Task 1: Audit and safety correctness

**Files:** Modify `tests/`; modify `backend/app/copilot/intent.py`, `backend/app/copilot/retrieval.py`, `gateway/simulator.py`, `backend/app/services/telemetry_service.py`; create `docs/FINAL-CODEX-AUDIT.md`.

**Interfaces:** Produces validated node extraction, metadata-aware retrieval, bounded simulator telemetry, and duplicate rejection results consumed by later services.

- [ ] Add focused regression tests for invalid explicit IDs, document ranking, metric bounds, disabled vision, and duplicate side effects.
- [ ] Run each test and confirm the expected failure.
- [ ] Implement the smallest source corrections.
- [ ] Run focused and full backend suites.

### Task 2: Authentication and authorization

**Files:** Modify configuration, authentication, API routers, WebSocket endpoint, frontend login/layout; add auth/RBAC tests.

**Interfaces:** Produces authenticated user/role dependencies and WebSocket token validation consumed by all protected operations.

- [ ] Add failing tests for bypass enabled/disabled, role restrictions, CORS, and WebSocket rejection.
- [ ] Implement explicit development bypass and permission dependencies.
- [ ] Protect operational routes and mutations by role.
- [ ] Render the bypass indicator and verify the suite.

### Task 3: Operational services

**Files:** Add readiness/gateway/evidence services and routes; modify telemetry, alerts, logs, reports, and WebSocket events.

**Interfaces:** Produces real readiness, gateway, event-evidence, report, and event contracts for frontend and Copilot.

- [ ] Add failing service/API tests for actual readiness, gateway freshness, evidence, exports, and required events.
- [ ] Implement services using persisted state rather than fixed green values.
- [ ] Verify simulator and serial adapters enter the same ingestion service.
- [ ] Run backend integration tests.

### Task 4: Copilot completion

**Files:** Modify Copilot intent, planner, tools, fallback, session, router, streaming, and frontend drawer; extend Copilot tests.

**Interfaces:** Consumes authenticated operational services; produces non-empty grounded chat and SSE contracts.

- [ ] Add failing tests for required English/Tanglish prompts, context, missing telemetry, invalid nodes, fallback, sources, sessions, and streaming cancellation semantics.
- [ ] Complete deterministic routing/tools and local fallback formatting.
- [ ] Complete session and streaming UI with source/deep-link metadata.
- [ ] Run all Copilot tests and the full backend suite.

### Task 5: Frontend resilience and missing pages

**Files:** Add Calibration and System Readiness pages, shared resilient-state components, route/API updates, and page tests.

**Interfaces:** Consumes readiness/calibration and common API error contracts.

- [ ] Configure Vitest and write failing route/state/accessibility tests.
- [ ] Add missing routes and visible loading, empty, error, retry, and offline states.
- [ ] Ensure mobile navigation, focus behavior, and semantic statuses.
- [ ] Run frontend tests and TypeScript build.

### Task 6: PWA, caching, and bundle optimization

**Files:** Modify service worker, manifest, app routes, API cache layer, and Vite configuration; add offline tests.

**Interfaces:** Produces labeled last-known data and lazy route chunks.

- [ ] Add failing tests for cache metadata and stale labeling.
- [ ] Implement bounded last-known-data storage and explicit data modes.
- [ ] Lazy-load route, map, chart, and Copilot boundaries.
- [ ] Build and record actual bundle sizes.

### Task 7: End-to-end and load verification

**Files:** Add Playwright configuration/specs and measured telemetry/Copilot load scripts.

**Interfaces:** Exercises the deployed frontend/backend contract.

- [ ] Add login, normal, flood, fire, landslide, Copilot, offline, and recovery journeys.
- [ ] Run available E2E paths or record browser-runtime blocker exactly.
- [ ] Run telemetry and Copilot load tests and record measured percentiles/error rates.
- [ ] Execute the prescribed SIH demo flow through APIs and WebSocket evidence.

### Task 8: Final polish and reporting

**Files:** Modify frontend presentation/accessibility styles and docs; create `docs/FINAL-READINESS-REPORT.md`.

**Interfaces:** Consumes all verified results and produces the final handoff.

- [ ] Apply restrained design-system and responsive polish after correctness is stable.
- [ ] Run backend suite, frontend suite, production build, and API smoke checks fresh.
- [ ] Record verified completion percentages, limitations, commands, URLs, and demo procedure.
- [ ] Perform a final independent review and address critical/important findings with tests.
