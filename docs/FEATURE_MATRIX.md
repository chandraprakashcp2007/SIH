# PRAHARI-NET V2 Feature Matrix

Status vocabulary: DONE, PARTIAL, NOT_CONFIGURED, PLANNED, BLOCKED. This file is the source of truth for demo claims and must be updated from executed evidence after every phase.

| Feature | Backend | DB | API | Frontend | Real Data | Simulation | Tests | Production | Evidence / Notes |
|---|---|---|---|---|---|---|---|---|---|
| Auth + RBAC | DONE | DONE | DONE | DONE | DONE | N/A | DONE | PARTIAL | Dev bypass must be disabled and secrets rotated in production |
| Legacy telemetry ingest | DONE | DONE | DONE | DONE | PARTIAL | DONE | DONE | PARTIAL | USB serial path exists; physical hardware not tested here |
| Provenance isolation | DONE | DONE | DONE | PARTIAL | DONE | DONE | DONE | PARTIAL | REAL/SIMULATION/EXTERNAL_DATA/REPLAY/PLANNED; UI coverage incomplete |
| Canonical Observation | DONE | DONE | DONE | PLANNED | PARTIAL | DONE | DONE | PARTIAL | Legacy telemetry adapter persists per-property observations; physical field validation remains pending |
| SensorThings subset | DONE | DONE | DONE | N/A | PARTIAL | DONE | DONE | PARTIAL | Read-only Things, Locations, Sensors, Datastreams and Observations mapping; not a complete SensorThings server |
| Geospatial dataset registry | DONE | DONE | DONE | PARTIAL | PARTIAL | DONE | DONE | PARTIAL | Registry and GeoJSON feature store implemented; STAC metadata catalog exposed as METADATA_ONLY |
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
| Secure telemetry + audit chain | DONE | DONE | DONE | DONE | NOT_CONFIGURED | PARTIAL | DONE | PARTIAL | Canonical HMAC envelopes, atomic persisted nonce/REAL-sequence replay defense, keyed-device legacy-ingress denial, rejection-before-mutation, secret non-disclosure checks and process-serialized hash chain; multi-instance database serialization and physical device keys remain unverified/NOT_CONFIGURED |
| Dataset manager + model registry | DONE | DONE | DONE | PARTIAL | NOT_CONFIGURED | PARTIAL | DONE | PARTIAL | Persisted manifest checks, model metadata and drift/OOD assessments; self-attestation cannot produce VALIDATED and no scientifically validated artifact is configured |
| Disaster memory + black box | PARTIAL | DONE | DONE | PARTIAL | NOT_CONFIGURED | PARTIAL | DONE | PLANNED | Deterministic fingerprints, provenance-scoped similarity, sequential checksum chain and isolated REPLAY projection; storage is not immutable, tail deletion lacks a trusted external head, evidence IDs are not authority-validated, and no historical corpus is configured |
| Scenario + Chaos Laboratories | PARTIAL | DONE | DONE | PARTIAL | N/A | PARTIAL | DONE | PLANNED | Persists deterministic SIMULATION-only manifests/hashes and proves no REAL mutation; isolated scenario execution and fault-injection engines are not implemented |
| Recovery + damage | DONE | DONE | DONE | PARTIAL | NOT_CONFIGURED | PARTIAL | DONE | PARTIAL | Authorized operator/admin evidence workflow, artifact-required human verification and evidence-ID-backed reports; SIMULATION/REPLAY/PLANNED cannot produce verified recovery and no automatic all-clear |
| Copilot 2.0 | PARTIAL | DONE | DONE | PARTIAL | PARTIAL | PARTIAL | DONE | PARTIAL | Narrow read-only TEL/RISK grounding endpoint cites internal IDs and abstains for unsupported provider/prediction/route/delivery questions, including when a node is named; full semantic claim/evidence coverage is not implemented |
| STAC metadata catalog | DONE | N/A | DONE | N/A | NOT_CONFIGURED | N/A | DONE | PARTIAL | STAC 1.0.0 catalog endpoint exposes dataset registry metadata only; explicitly METADATA_ONLY with no live-provider claim |
| DDQI + Assurance | PARTIAL | DONE | DONE | DONE | NOT_CONFIGURED | N/A | DONE | PLANNED | Persists an explicit DDQI 0 / UNVERIFIED snapshot and unverified safety-case assertions with blockers; no measured DDQI methodology or independent assurance evidence exists |
| Phase 19 production-readiness review | DONE | N/A | N/A | N/A | N/A | N/A | DONE | BLOCKED | Local review complete; exact Railway, migration, secrets, provider, hardware, validation, delivery, observability and smoke-test gates documented |
| Railway deployment | PARTIAL | PARTIAL | DONE | DONE | NOT_CONFIGURED | DONE | PARTIAL | BLOCKED | Requires deployment permission and production smoke test |
