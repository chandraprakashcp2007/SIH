# PRAHARI-NET Final Hardening Design

## Intent

Finish the existing PRAHARI-NET repository as a reliable SIH emergency-operations product while preserving its React/Vite, FastAPI, SQLite, WebSocket, simulator, serial gateway, risk-engine, and Copilot architecture.

## Constraints

- Never replace working subsystems or create duplicate applications.
- Local telemetry, risk, alerts, persistence, WebSocket updates, simulator operation, and Copilot fallback must work without internet.
- Simulated and serial telemetry use the same backend ingestion service.
- Hazard decisions remain deterministic and separate from Copilot.
- Vision-disabled operation must not fabricate camera evidence.
- Development authentication bypass is explicit, visible, and disabled safely by configuration.
- Stale or cached data is never presented as live data.
- Verification claims require current test, build, API, or browser evidence.

## Architecture

The existing backend remains the authority. Telemetry enters through a validated packet boundary, is deduplicated before risk evaluation, then produces persisted telemetry, risk, trust, event evidence, alerts, gateway health, audit logs, and real-time events. Authentication dependencies enforce role permissions at API boundaries; WebSocket authentication uses the same signed token model.

The frontend remains one React application. A shared API/state layer reports loading, empty, error, cached, simulation, and edge-mode states. Routes are lazy-loaded. Calibration and Readiness become first-class pages, while hazard intelligence stays in the existing node-detail view with explicit JALA, AGNI, and BHUMI navigation.

Copilot keeps its deterministic fast path and read-only tools. Explicit node IDs are validated before aliases, retrieval includes document metadata, every non-empty valid message receives a safe local response, sessions persist, and streaming returns operational status without hidden reasoning.

## Delivery Slices

1. Audit baseline and safety regressions.
2. Telemetry, simulator, vision, duplicate, Copilot entity, and retrieval correctness.
3. Development bypass, authentication, RBAC, WebSocket authentication, and configured CORS.
4. Gateway/readiness/evidence/logging/reporting and real-time event completion.
5. Missing frontend routes, resilient request states, Copilot UI, and offline/PWA behavior.
6. Route code splitting, frontend tests, E2E coverage, UI polish, demo validation, and measured load tests.

## Error Handling and Security

Malformed or duplicate packets are rejected before evaluation and persistence with stable machine-readable responses. APIs return safe error details without credentials or stack traces. Operator and viewer reads are separated from operator alert actions and admin simulator/settings/calibration actions. Local bypass tokens identify bypass mode visibly and never activate unless `DEV_AUTH_BYPASS=true`.

## Verification

Backend unit/integration tests cover each safety invariant. Frontend component tests cover routing and resilient states. Playwright covers authentication, normal and hazard scenarios, Copilot, offline mode, and recovery. Production builds report chunk sizes. Load scripts report measured p50, p95, p99, and error rate. Visual browser inspection is completed only when browser tooling is available and otherwise remains explicitly pending.
