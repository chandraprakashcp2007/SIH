# PRAHARI-NET Testing & Validation Guide

## Test Architecture

The automated test suite verifies:
1. **API Integration Tests (`tests/test_api_integration.py`):** REST endpoints, telemetry ingestion, WebSocket connectivity.
2. **AI Risk Engine Tests (`tests/test_risk_engine.py`):** JALA hydrograph escalation, AGNI false alarm suppression, BHUMI shear slip.
3. **Sensor Trust Tests (`tests/test_trust.py`):** Transducer bounds, frozen sensor detection, kinematic jump checks.
4. **Copilot Intent Tests (`tests/test_copilot_intents.py`):** Classification across 14 operational query categories.
5. **Copilot Fast-Path Tests (`tests/test_copilot_fast_path.py`):** Sub-200ms deterministic response verification.
6. **Copilot RAG Retrieval Tests (`tests/test_copilot_rag.py`):** Inverted index, BM25 ranking, and fingerprint cache.
7. **Copilot Safety Tests (`tests/test_copilot_safety.py`):** Prompt injection defense, secret masking, read-only enforcement.
8. **Copilot Failover Tests (`tests/test_copilot_failover.py`):** Graceful degradation to Local Assistant on LLM timeout.
9. **Load Testing Benchmark (`scripts/load-test-copilot.py`):** 50 concurrent operational queries measuring p50, p95, and p99 latency.

## Executing Tests

```powershell
python -m pytest tests/ -v
python scripts/load-test-copilot.py
```
