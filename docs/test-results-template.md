# PRAHARI-NET System Performance & Benchmark Record

**Date:** September 2026  
**Environment:** Windows 11 / Python 3.13 / SQLite WAL / React 19 Frontend  
**Test Suite:** Pytest + High-Throughput Stress Ingestion Script (`scripts/stress-demo.py`)  

---

## 1. Automated Test Results

| Test Category | Suite File | Total Tests | Passed | Failed | Execution Time |
|---|---|---|---|---|---|
| Security & Cryptography | `tests/test_auth.py` | 3 | 3 | 0 | 0.05s |
| Risk Engine & Multi-Sensor Fusion | `tests/test_risk_engine.py` | 5 | 5 | 0 | 0.85s |
| Sensor Trust & Fault Isolation | `tests/test_trust.py` | 3 | 3 | 0 | 0.12s |
| REST API & Ingestion Endpoints | `tests/test_api_integration.py` | 5 | 5 | 0 | 1.53s |
| **Total Test Suite** | | **16** | **16** | **0** | **2.55s** |

---

## 2. Ingestion & Pipeline Benchmarking (Measured)

*Measured via `python scripts/stress-demo.py` against active local backend on `http://127.0.0.1:8000`.*

| Metric | Target Specification | Measured Result | Evaluation |
|---|---|---|---|
| Total Ingested Packets | 1,000 | 1,000 | 100% Complete |
| Ingestion Success Rate | > 99.5% | 100.0% | PASS |
| Sustained Throughput | > 50 pkts/sec | ~180-240 pkts/sec | Exceeds Requirement |
| Mean Ingestion Latency | < 50 ms | ~4.2 ms | PASS (High Performance) |
| 95th Percentile Latency | < 100 ms | ~9.8 ms | PASS |
| WebSocket Latency | < 20 ms | ~1.5 ms | PASS |
| DB Write Lock Contention | 0 Errors | 0 Errors (SQLite WAL) | PASS |
