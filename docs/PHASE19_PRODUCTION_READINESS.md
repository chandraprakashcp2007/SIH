# Phase 19 Production-Readiness Review

Date: 2026-09-27

## Verdict

Local acceptance is complete, but Railway production deployment is **BLOCKED**. No deploy or remote push is authorized by this phase. The system is suitable for a labelled local demonstration; it is not verified for unattended emergency-response production use.

## Implemented locally

- Phase 0–17 capabilities and Phase 18 regression/security/provenance/E2E gates.
- Root multi-stage production Dockerfile and authenticated FastAPI/React build.
- Truthful NOT_CONFIGURED, PLANNED and BLOCKED states for unavailable integrations.
- Additive SQLAlchemy schema creation for isolated/local databases.

## Known local limitations retained as partial

- Disaster-memory checksum chaining is tamper-evident only for the retained sequence; it is not immutable storage and has no external trusted head.
- Scenario/chaos APIs persist deterministic manifests and isolation evidence but do not execute an isolated scenario or fault-injection engine.
- Copilot 2.0 has narrow TEL/RISK grounding rather than a complete semantic evidence-query layer.
- DDQI and safety assertions remain UNVERIFIED; no synthetic assurance score is presented.
- Security-event appends are serialized within one application process; production multi-instance serialization must be enforced by the production database design and tested before deployment.

## Production blockers and external dependencies

1. Railway project/environment credentials and deployment permission are absent; no production smoke test exists.
2. Production PostgreSQL is not provisioned, backed up or restore-tested. There is no Alembic migration chain; `create_all` is not an adequate production migration/rollback mechanism.
3. `SECRET_KEY` must be supplied from a secret manager, `DEV_AUTH_BYPASS=false` must be enforced, production CORS origins must be explicit, and TLS/DNS must be verified.
4. Physical ESP32/sensor, LoRa, serial gateway and SIM800L paths are not field-verified; device keys are NOT_CONFIGURED.
5. Authoritative DEM, population, infrastructure, hydrology, FIRMS/weather/government feeds and historical disaster corpora are not configured/licensed/validated.
6. No scientifically validated model artifact or reproducible validation dataset is configured; model outputs must continue to abstain or remain labelled prototype heuristics.
7. Official CAP/NDMA/SACHET/SMS delivery authority and provider receipts are not configured.
8. Production observability, alerting, retention, incident response, load target/SLO, security review and disaster-recovery exercises require deployment-owner evidence.

## Exact work before Railway deployment

1. Obtain deployment approval and Railway access; provision managed PostgreSQL and persistent backup/restore procedures.
2. Add and rehearse versioned migrations against a sanitized production-like clone; document forward and rollback procedures.
3. Configure rotated secrets, device-key storage, `DEV_AUTH_BYPASS=false`, exact CORS origins, TLS/DNS and least-privilege gateway/operator accounts.
4. Configure only licensed authoritative providers/datasets, validate checksums/licences/freshness, and keep all others NOT_CONFIGURED.
5. Perform hardware/field calibration and end-to-end LoRa/serial/SIM800L tests; do not promote SIMULATION evidence to REAL.
6. Establish reproducible model-validation artifacts or keep model registry entries UNVALIDATED with abstention.
7. Configure an authorized warning-delivery provider and verify receipts without claiming delivery beforehand.
8. Define production SLOs and run representative PostgreSQL load, soak, failover, backup-restore and security tests.
9. Deploy a candidate, run authenticated API/WebSocket/browser smoke tests, verify migrations and observability, and record the deployment URL/commit/result.

Operational `data/prahari.db` was not opened for test writes; its final SHA-256 is recorded in the Phase 18 evidence and final handoff.
