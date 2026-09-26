# PRAHARI-NET V2 Feature Matrix

Status vocabulary: DONE, PARTIAL, NOT_CONFIGURED, PLANNED, BLOCKED. This file is the source of truth for demo claims and must be updated from executed evidence after every phase.

| Feature | Backend | DB | API | Frontend | Real Data | Simulation | Tests | Production | Evidence / Notes |
|---|---|---|---|---|---|---|---|---|---|
| Auth + RBAC | DONE | DONE | DONE | DONE | DONE | N/A | DONE | PARTIAL | Dev bypass must be disabled and secrets rotated in production |
| Legacy telemetry ingest | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | USB serial path exists; physical hardware not tested here |
| Provenance isolation | DONE | DONE | DONE | PARTIAL | DONE | DONE | DONE | PARTIAL | REAL/SIMULATION/EXTERNAL_DATA/REPLAY/PLANNED; UI coverage incomplete |
| Canonical Observation | DONE | DONE | DONE | PLANNED | PARTIAL | DONE | DONE | PARTIAL | Legacy telemetry adapter persists per-property observations; physical field validation remains pending |
| SensorThings subset | DONE | DONE | DONE | N/A | PARTIAL | DONE | DONE | PARTIAL | Read-only Things, Locations, Sensors, Datastreams and Observations mapping; not a complete SensorThings server |
| Geospatial dataset registry | DONE | DONE | DONE | PARTIAL | PARTIAL | DONE | DONE | PARTIAL | Registry and GeoJSON feature store implemented; STAC expansion remains Phase 17 |
| JALA map | DONE | DONE | DONE | DONE | NOT_CONFIGURED | DONE | DONE | PARTIAL | Dedicated route and backend layers; river/basin/forecast datasets unavailable |
| AGNI map | DONE | DONE | DONE | DONE | NOT_CONFIGURED | DONE | DONE | PARTIAL | Dedicated route; FIRMS remains NOT_CONFIGURED |
| BHUMI map | DONE | DONE | DONE | DONE | NOT_CONFIGURED | DONE | DONE | PARTIAL | Dedicated route; DEM remains NOT_CONFIGURED |
| VAYU map | DONE | DONE | DONE | DONE | NOT_CONFIGURED | DONE | DONE | PARTIAL | Dedicated route; PM values visibly simulation-only |
| AKASHA map | DONE | DONE | DONE | DONE | NOT_CONFIGURED | DONE | DONE | PARTIAL | Dedicated route; authoritative weather providers remain NOT_CONFIGURED |
| Historical graphs | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | Database aggregation supports 15m, 1h, 6h, 24h and 7d; legacy node charts remain compatible |
| Sensor trust | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | Persisted per-sensor snapshots, reason codes and fleet dashboard; calibrated field validation pending |
| Evidence fusion | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | DONE | DONE | PLANNED | Immediate risk evidence exists; canonical evidence item graph absent |
| Evidence Gate | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | Persisted 15-check hazard/severity policies, confidence decay and why-withheld explanations; authoritative/model evidence remains unavailable where not configured |
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
