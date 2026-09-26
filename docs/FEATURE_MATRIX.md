# PRAHARI-NET V2 Feature Matrix

Status vocabulary: DONE, PARTIAL, NOT_CONFIGURED, PLANNED, BLOCKED. This file is the source of truth for demo claims and must be updated from executed evidence after every phase.

| Feature | Backend | DB | API | Frontend | Real Data | Simulation | Tests | Production | Evidence / Notes |
|---|---|---|---|---|---|---|---|---|---|
| Auth + RBAC | DONE | DONE | DONE | DONE | DONE | N/A | DONE | PARTIAL | Dev bypass must be disabled and secrets rotated in production |
| Legacy telemetry ingest | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | USB serial path exists; physical hardware not tested here |
| Provenance isolation | DONE | DONE | DONE | PARTIAL | DONE | DONE | DONE | PARTIAL | REAL/SIMULATION/EXTERNAL_DATA/REPLAY/PLANNED; UI coverage incomplete |
| Canonical Observation | PLANNED | PLANNED | PLANNED | PLANNED | NOT_CONFIGURED | PLANNED | PLANNED | PLANNED | Phase 1 |
| SensorThings subset | PLANNED | PARTIAL | PLANNED | N/A | NOT_CONFIGURED | PARTIAL | PLANNED | PLANNED | Domain registry resembles Things but no interop routes |
| Geospatial dataset registry | PARTIAL | PARTIAL | PARTIAL | PARTIAL | NOT_CONFIGURED | PARTIAL | PARTIAL | PLANNED | External dataset metadata exists; full layer/STAC registry absent |
| JALA map | PARTIAL | PARTIAL | PARTIAL | PARTIAL | NOT_CONFIGURED | DONE | PARTIAL | PLANNED | Shared map only; no validated river/basin/forecast datasets |
| AGNI map | PARTIAL | PARTIAL | PARTIAL | PARTIAL | NOT_CONFIGURED | DONE | PARTIAL | PLANNED | FIRMS not configured |
| BHUMI map | PARTIAL | PARTIAL | PARTIAL | PARTIAL | NOT_CONFIGURED | DONE | PARTIAL | PLANNED | DEM unavailable |
| VAYU map | PARTIAL | PARTIAL | PARTIAL | PARTIAL | NOT_CONFIGURED | DONE | PARTIAL | PLANNED | PM values are simulation only; no calibrated PM hardware |
| AKASHA map | PARTIAL | PARTIAL | PARTIAL | PARTIAL | NOT_CONFIGURED | DONE | PARTIAL | PLANNED | Weather providers not configured |
| Historical graphs | DONE | DONE | DONE | DONE | PARTIAL | DONE | PARTIAL | PARTIAL | Persisted history; required aggregation windows incomplete |
| Sensor trust | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | Fleet digital twin/fault history incomplete |
| Evidence fusion | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | DONE | DONE | PLANNED | Immediate risk evidence exists; canonical evidence item graph absent |
| Evidence Gate | PLANNED | PLANNED | PLANNED | PLANNED | NOT_CONFIGURED | PLANNED | PLANNED | PLANNED | No persisted hazard-specific 15-check policy engine |
| Predictions | PARTIAL | DONE | DONE | DONE | NOT_CONFIGURED | DONE | PARTIAL | PLANNED | Deterministic heuristics; MODEL NOT VALIDATED |
| Cross-hazard cascades | PLANNED | PLANNED | PLANNED | PLANNED | NOT_CONFIGURED | PLANNED | PLANNED | PLANNED | Phase 5 |
| Compound risk | PLANNED | PLANNED | PLANNED | PLANNED | NOT_CONFIGURED | PLANNED | PLANNED | PLANNED | Phase 5 |
| Upstream propagation | PLANNED | PLANNED | PLANNED | PLANNED | NOT_CONFIGURED | PLANNED | PLANNED | PLANNED | River topology/flow parameters absent |
| Time-to-impact | PARTIAL | PARTIAL | PARTIAL | PARTIAL | NOT_CONFIGURED | PARTIAL | PARTIAL | PLANNED | Existing crossing estimate is not a validated hydrodynamic model |
| Alerts | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | Local lifecycle only |
| CAP 1.2 | PLANNED | PLANNED | PLANNED | PLANNED | NOT_CONFIGURED | PLANNED | PLANNED | PLANNED | No official delivery integration |
| External providers | PARTIAL | DONE | DONE | DONE | NOT_CONFIGURED | N/A | DONE | PLANNED | Registrations/manual import foundation; no verified live provider |
| Offline PWA cache | PARTIAL | N/A | N/A | DONE | PARTIAL | DONE | PARTIAL | PARTIAL | Read cache exists; durable mutation/outbound queue absent |
| Secure telemetry | PARTIAL | PARTIAL | PARTIAL | PARTIAL | NOT_CONFIGURED | PARTIAL | PARTIAL | PLANNED | JWT gateway auth exists; signatures/nonces/key rotation absent |
| Model registry | PLANNED | PLANNED | PLANNED | PLANNED | NOT_CONFIGURED | PLANNED | PLANNED | PLANNED | No validated artifacts |
| Scenario Lab | PARTIAL | PARTIAL | DONE | DONE | N/A | DONE | DONE | PARTIAL | Existing simulator is labelled; comparison isolation incomplete |
| Recovery + damage | PLANNED | PLANNED | PLANNED | PLANNED | NOT_CONFIGURED | PLANNED | PLANNED | PLANNED | Phase 15 |
| Copilot | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | Grounded/read-only; live paid provider not verified |
| Railway deployment | PARTIAL | PARTIAL | DONE | DONE | NOT_CONFIGURED | DONE | PARTIAL | BLOCKED | Requires deployment permission and production smoke test |

