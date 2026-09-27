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
| Cross-hazard cascades | DONE | DONE | DONE | DONE | NOT_CONFIGURED | DONE | DONE | PARTIAL | Persisted configured reevaluation relationships, typed event, evidence references and explicit non-causation UI; authoritative field inputs unavailable |
| Compound risk | DONE | DONE | DONE | DONE | NOT_CONFIGURED | DONE | DONE | PARTIAL | Versioned transparent band rules; no arithmetic risk-score blending; field validation unavailable |
| Regional consensus | DONE | DONE | DONE | DONE | NOT_CONFIGURED | PARTIAL | DONE | PARTIAL | Weighting interface persisted; current topology truthfully reports INSUFFICIENT_NEIGHBOURS instead of manufacturing peers |
| Operational digital twin | DONE | DONE | DONE | DONE | NOT_CONFIGURED | DONE | DONE | PARTIAL | Persisted snapshots and events; confidence/uncertainty shown separately and missing validated boundary layers exposed as blind spots |
| Impact, dependencies, evacuation + safe zones | DONE | DONE | DONE | DONE | NOT_CONFIGURED | PARTIAL | DONE | PARTIAL | Interfaces, persisted assessments, events and UI implemented; exposure counts/routes/zones withheld until authoritative datasets and field verification exist |
| Upstream propagation | DONE | DONE | DONE | DONE | NOT_CONFIGURED | PARTIAL | DONE | PARTIAL | River topology registry, downstream assessment/event and UI implemented; authoritative topology remains NOT_CONFIGURED |
| Time-to-impact | DONE | DONE | DONE | DONE | NOT_CONFIGURED | PARTIAL | DONE | PARTIAL | Downstream travel time is UNAVAILABLE until imported reaches carry validated travel-time parameters; legacy local threshold projection remains explicitly separate |
| Alerts | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | Local lifecycle only |
| CAP 1.2 | DONE | DONE | DONE | DONE | NOT_CONFIGURED | DONE | DONE | PARTIAL | Schema-contract CAP-compatible XML with English/Hindi templates and lifecycle mapping; official delivery channels remain NOT_CONFIGURED and never report delivery without provider receipts |
| External providers | PARTIAL | DONE | DONE | DONE | NOT_CONFIGURED | N/A | DONE | PLANNED | Registrations/manual import foundation; no verified live provider |
| Offline continuity | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | Persisted checksum-idempotent store-and-forward queue, replay-safe acknowledgement, derived link/energy policies and explicit stale cache labels; hardware transports retain truthful capability states |
| Secure telemetry + audit chain | DONE | DONE | DONE | DONE | NOT_CONFIGURED | PARTIAL | DONE | PARTIAL | Canonical HMAC envelopes, server-side key configuration, persisted nonce and REAL-sequence replay defense before operational mutation, persisted rejection events, secret non-disclosure checks and verifiable hash chain; physical device keys remain NOT_CONFIGURED |
| Dataset manager + model registry | DONE | DONE | DONE | DONE | NOT_CONFIGURED | PARTIAL | DONE | PARTIAL | Persisted manifest validation, model validation evidence, drift/OOD assessments and mandatory abstention; no scientifically validated artifacts are configured |
| Disaster memory + black box | DONE | DONE | DONE | DONE | NOT_CONFIGURED | DONE | DONE | PARTIAL | Deterministic hazard fingerprints, evidence-ID-linked similarity, verifiable hash chain and read-only REPLAY projection; no historical authoritative corpus configured |
| Scenario + Chaos Laboratories | DONE | DONE | DONE | DONE | N/A | DONE | DONE | PARTIAL | Deterministic seeded run records and confined fault injection; explicit tests prove no REAL telemetry mutation or strengthening |
| Recovery + damage | DONE | DONE | DONE | DONE | NOT_CONFIGURED | PARTIAL | DONE | PARTIAL | Persisted provenance-labelled damage evidence, mandatory human-verification state and evidence-ID-backed incident reports; never auto all-clear |
| Copilot | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | Grounded/read-only; live paid provider not verified |
| Railway deployment | PARTIAL | PARTIAL | DONE | DONE | NOT_CONFIGURED | DONE | PARTIAL | BLOCKED | Requires deployment permission and production smoke test |
