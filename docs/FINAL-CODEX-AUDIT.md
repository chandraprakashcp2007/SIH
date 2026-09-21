# PRAHARI-NET Final Codex Audit

Date: 2026-09-21  
Scope: incremental hardening of the existing SIH repository, preserving its architecture and data.

| Module | Status | Working | Partial | Broken | Missing | Action required |
|---|---|---|---|---|---|---|
| Telemetry ingestion | VERIFIED | Shared service for HTTP, simulator and serial; duplicate packets exit before persistence/risk/alerts/events | Process-local sequence memory resets on restart; DB uniqueness remains the durable backstop | None found in tests | Distributed idempotency store | Add Redis/Postgres idempotency for multi-instance deployment |
| Simulator safety | VERIFIED | Non-negative rain/environment values; bounded percentages; no camera confidence when vision is disabled | Synthetic realism is deterministic/demo-oriented | None found | Physical sensor calibration data | Validate ranges against field hardware |
| Risk/alert pipeline | VERIFIED | Feature extraction, trust, fusion, risk, evidence and alert lifecycle execute in one pipeline | SQLite and demo thresholds are not certified safety infrastructure | None found | Formal hazard-model validation | Field-calibrate and obtain domain review before real emergency use |
| Authentication | VERIFIED FOR LOCAL DEMO | Signed JWT, database auth when bypass disabled, explicit local bypass banner | Local `.env` deliberately enables bypass | None found | Secret manager/rotation | Disable bypass and replace secret for production |
| RBAC | VERIFIED | Operational APIs require auth; telemetry is ADMIN/GATEWAY; simulator/settings/calibration are ADMIN; alert mutation is ADMIN/OPERATOR | Read-only APIs intentionally shared by authenticated roles | None found | Enterprise identity federation | Add OIDC if deploying beyond the demo |
| WebSocket | VERIFIED | Authenticated handshake, typed events, reconnect, bearer kept out of URL via subprotocol | Single-process connection registry | None found | Cross-instance pub/sub | Add Redis/NATS for horizontal scaling |
| CORS | VERIFIED | Environment-configured allowlist | Defaults target local development | None found | Deployment-specific origins | Set exact production origins |
| Gateway status | VERIFIED | Derived from latest packet time as CONNECTED/STALE/OFFLINE | Timeout is fixed at 10 seconds in service default | None found | Per-deployment timeout setting | Externalize timeout if field cadence differs |
| Readiness | VERIFIED | Database, gateway, nodes, backend, WebSocket, risk, alerts, audio, PWA, Copilot, KB and simulator checks | Several checks validate loaded capability, not an external synthetic transaction | None found | Deep serial loopback | Add hardware loopback probe on deployment target |
| Evidence/exports | VERIFIED | Alert evidence envelope; incident report; telemetry/alerts/events CSV | Events use audit-log storage rather than a dedicated event table | None found | Signed evidence bundles | Add signatures/retention policy if legally required |
| Copilot entity resolution | VERIFIED | Explicit IDs are preserved; JALA-99 returns not found and never becomes JALA-01 | Alias vocabulary is finite | None found | Broader multilingual NLU corpus | Expand only with regression fixtures |
| Copilot grounding/RAG | VERIFIED | Entity-aware metadata ranking and source attribution | Local lexical retrieval, not vector search | None found | Embedding index | Optional; retain deterministic provenance boost |
| Copilot operations | VERIFIED | Live tools, fast paths, Tanglish intents, sessions, SSE streaming, fallback, sources, timestamps, copy, stop, recent chats, deep links | External AI path was tested with mocks, not a live paid provider credential | None found | Live provider credential validation | Run a provider smoke test when credentials exist |
| Copilot session privacy | VERIFIED | Session reads/deletes scoped to owner; admin can inspect | Admin visibility is intentional | None found | Retention UI | Define retention policy |
| Calibration page | VERIFIED | Admin-only persisted calibration settings and UI | Values are configuration, not instrument-certified | None found | Calibration certificate workflow | Add field validation/certificates for production |
| System Readiness page | VERIFIED | Live state, retry, error and responsive UI | No automated physical serial test | None found | Hardware loopback | Validate on gateway laptop |
| Frontend resilience | SUBSTANTIAL | Route suspense, readiness loading/error/retry, cached-data warning, offline banner, responsive navigation, keyboard focus and reduced motion | Some legacy pages still have page-specific rather than uniform retry/empty components | No blocking defect found in tested flows | Central error boundary and uniform query layer | Recommended next hardening increment |
| PWA/offline | SUBSTANTIAL | Service worker shell caching, navigation fallback, last-known operational cache, CACHED and LOCAL EDGE labels | Not every historical/report payload is retained offline | None found in tested core display | Full offline mutation queue | Keep operational actions disabled offline |
| Bundle | VERIFIED | Route lazy loading and separate page/chart chunks | Chart drawer remains a 162.35 kB chunk | No >500 kB bundle warning | Further vendor partitioning | Optional; current main gzip is 77.58 kB |
| Automated tests | VERIFIED | 68 backend, 4 frontend unit, 4 Playwright desktop/mobile | No physical hardware test | None at final run | Cross-browser Safari/Firefox | Add in CI if target scope expands |
| Hardware integration | CODE-READY / FIELD-PENDING | Serial and simulator feed exact same ingestion endpoint/service; gateway authenticates | No COM/LoRa device was available in this environment | Not claimed as physically verified | Real serial/LoRa validation | Connect target gateway and execute protocol checklist |
| Deployment | LOCAL-DEMO READY | Reproducible PowerShell startup and local URLs | SQLite/single-process architecture | None for local SIH demo | HA, TLS termination, backups | Required before production use |

## Correctness defects closed

1. Explicit unknown node IDs can no longer alias to a known node; unknown-node answers do not fabricate a NORMAL state.
2. RAG ranking now favors entity-matched authoritative documents.
3. Simulator environmental values are clamped to physically valid domains.
4. Vision evidence is omitted when vision is disabled.
5. Duplicate packets are detected before every side effect.
6. Gateway/readiness status is derived rather than hardcoded.
7. The mobile drawer closes after navigation and no longer blocks page controls.
8. WebSocket bearer material is no longer placed in request URLs.

## Known limitations

- The repository still has no baseline Git commit and all original content remains untracked; no destructive cleanup or reset was performed.
- Physical serial/LoRa hardware, camera input, and live external-LLM credentials were unavailable, so those integrations are code-ready but not field-certified.
- SQLite is appropriate for the local demo, not high-availability multi-instance deployment.
- Offline mode provides last-known operational visibility, not offline writes or alert acknowledgement queues.
- The in-app browser connector was unavailable; Chromium desktop/mobile verification was completed with local Playwright instead.
