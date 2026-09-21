# PRAHARI COPILOT Architectural Upgrade Audit

**Platform:** PRAHARI-NET (Predictive Resilient Autonomous Hazard & Risk Intelligence Network)  
**Competition:** Smart India Hackathon 2026 — Problem Statement SIH26178  
**Date:** September 2026  
**Auditor:** Principal Software Architect & Lead Systems Engineer  

---

## 1. Executive Summary

This audit evaluates the codebase prior to the PRAHARI COPILOT architectural refactoring. The goal is to identify all existing, missing, broken, duplicated, refactor-required, and production-ready modules, ensuring zero regression to the operational hazard intelligence pipeline while upgrading Copilot into an emergency operations assistant.

---

## 2. Component-by-Component Assessment

### 2.1 Backend Core & Server Lifespan
- **Status:** `GOOD AS-IS`
- **Location:** `backend/app/main.py`, `backend/app/core/database.py`
- **Details:** 
  - FastAPI asynchronous server with lifespan context manager.
  - SQLAlchemy 2.0 with `aiosqlite` and SQLite WAL mode (`./data/prahari.db`).
  - Automatic seed initialization and background simulator loop start/stop.
  - Clean CORS handling and WebSocket mount at `/ws/live`.

### 2.2 Configuration & Environment Variables
- **Status:** `BROKEN / NEEDS REFACTOR`
- **Location:** `backend/app/core/config.py`
- **Defect:** 
  - On Windows development environments, the OS environment variable `DEBUG` is often preset by build tools to non-boolean strings like `"release"`.
  - Pydantic Settings parses `DEBUG: bool = False` by attempting strict boolean coercion, raising `pydantic_core._pydantic_core.ValidationError: Input should be a valid boolean, unable to interpret input 'release'`.
- **Remediation:** 
  - Implement a `@field_validator("DEBUG", mode="before")` or accept `Union[bool, str]` coercing `'release'`, `'0'`, `'false'` to `False`.
  - Add explicit configuration fields for Copilot: `COPILOT_ENABLED`, `COPILOT_MODE`, `COPILOT_FAST_PATH`, `COPILOT_STREAMING`, `COPILOT_CACHE_ENABLED`, `COPILOT_TOOL_TIMEOUT_MS`, `COPILOT_MAX_CONTEXT_CHUNKS`, `COPILOT_MAX_HISTORY_MESSAGES`, `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`, `LLM_TIMEOUT_SECONDS`, and `RAG_ENABLED`.

### 2.3 Physical Hazard & Risk Engine Pipeline
- **Status:** `GOOD AS-IS (PROTECTED AUTHORITATIVE LAYER)`
- **Location:** `backend/app/ai/risk_engine.py`, `backend/app/ai/trust.py`, `backend/app/ai/features.py`, `backend/app/ai/anomaly.py`, `backend/app/ai/fusion.py`, `backend/app/ai/explainability.py`, `backend/app/ai/prediction.py`
- **Details:** 
  - Authoritative hazard computation pipeline:
    `Sensors -> Features -> Sensor Trust -> Anomaly Detection -> Multi-Sensor Fusion -> Risk Engine -> Explainability -> Alert Service`.
  - Thoroughly tested with 100% test pass rate in `tests/test_risk_engine.py` and `tests/test_trust.py`.
  - **Absolute Safety Rule:** Copilot must NEVER overwrite, modify, or recalculate these values. Copilot is strictly read-only.

### 2.4 Physical Simulator & Hardware Gateway
- **Status:** `GOOD AS-IS`
- **Location:** `gateway/simulator.py`, `gateway/serial_bridge.py`, `backend/app/services/simulation_service.py`
- **Details:** 
  - Accurately models 14 disaster scenarios across JALA-01 (Flood), AGNI-02 (Fire/Combustion), and BHUMI-03 (Landslide/Slope Shear).
  - Telemetry frames adhere to standard protocol format.
  - Copilot must distinguish between `REAL` and `SIMULATION` data modes and label responses accordingly.

### 2.5 Real-Time Telemetry & Alert Ingestion Services
- **Status:** `GOOD AS-IS`
- **Location:** `backend/app/services/telemetry_service.py`, `backend/app/services/alert_service.py`, `backend/app/websocket/manager.py`
- **Details:** 
  - Ingests packets from serial or simulator, runs the risk engine, writes to database, logs sequence gaps, and broadcasts WebSocket events.
  - Manages alert lifecycle: `NEW -> ACKNOWLEDGED -> MONITORING -> RESOLVED`.

### 2.6 Existing Copilot Implementation
- **Status:** `NEEDS REFACTOR`
- **Location:** `backend/app/copilot/engine.py`
- **Limitations:** 
  - Only a 238-line single file with 4 rudimentary regex `if/elif` checks.
  - Lacks tool registry, parallel tool execution, RAG retrieval, session persistence, conversation memory, pronoun resolution, structured card responses, prompt injection defenses, streaming, or external LLM provider failover.
- **Remediation:** 
  - Replace with the comprehensive modular package: `backend/app/copilot/` with separate routers, orchestrator, intent classifier, tool registry, tool executor, local RAG retriever, context builder, grounding verifier, safety guardrails, streaming generator, session store, and provider adapters.

### 2.7 Copilot API Endpoints
- **Status:** `NEEDS REFACTOR`
- **Location:** `backend/app/api/copilot.py`
- **Limitations:** 
  - Exposes only a single `POST /api/copilot/chat` endpoint returning `{ reply, grounded, provider }`.
- **Missing Endpoints:** 
  - `GET /api/copilot/stream` (SSE real-time streaming)
  - `GET /api/copilot/health` (readiness & operational check)
  - `GET /api/copilot/metrics` (latency, counters, fast-path ratio)
  - `GET /api/copilot/sessions` & `POST /api/copilot/sessions` & `DELETE /api/copilot/sessions/{id}`
  - `GET /api/copilot/sessions/{id}/messages`
  - `POST /api/copilot/feedback` (operator thumbs up/down)
  - `GET /api/copilot/suggestions` (dynamic prompt suggestions)

### 2.8 Database Models for Copilot
- **Status:** `MISSING`
- **Location:** `backend/app/models/`
- **Required New Models:** 
  - `ChatSession`
  - `ChatMessage`
  - `CopilotToolCall`
  - `CopilotFeedback`
  - `CopilotMetric`
  - Proper index coverage on session, message timestamps, and tool calls.

### 2.9 Project Knowledge Base & Documentation for RAG
- **Status:** `MISSING / INCOMPLETE`
- **Location:** Root & `docs/`
- **Defects:** 
  - Root `README.md` is missing.
  - Node-specific architecture files (`docs/jala.md`, `docs/agni.md`, `docs/bhumi.md`, `docs/risk-engine.md`, `docs/gateway-protocol.md`, `docs/deployment.md`, `docs/demo-guide.md`, `docs/safety-limitations.md`, `docs/testing.md`) are missing.
- **Remediation:** 
  - Author complete, technically rich markdown files to be chunked and indexed into the local BM25 knowledge retriever.

### 2.10 Frontend Copilot UI / UX
- **Status:** `NEEDS REFACTOR`
- **Location:** `frontend/src/components/copilot/CopilotDrawer.tsx`
- **Defects:** 
  - Basic small floating popup (`380px`) with simple text bubbles.
  - No SSE token streaming or operational step progress.
  - No source chips (`LIVE TELEMETRY`, `RISK ENGINE`, etc.).
  - No structured cards for risk summaries, alert evidence, node comparisons, mini telemetry charts, or deep action links.
  - No session management (new chat, session history, search).
  - Inadequate mobile layout for standard 390x844 viewports.

---

## 3. Action Plan & Isolation Guarantees

1. **Safety Isolation:** Copilot modules run in `backend/app/copilot/` with strict read-only tool contracts. If Copilot crashes or times out, telemetry ingestion and the authoritative risk engine remain 100% unaffected.
2. **Deterministic Fast Path:** Common operational queries bypass LLMs completely to achieve `< 200ms` p95 response times.
3. **Local Assistant Sovereignty:** Offline edge functionality is guaranteed without cloud reliance or external API keys.
