# Phase 18 Local Acceptance Evidence

Date: 2026-09-27

All database-mutating verification used process-specific pytest databases, `data/prahari_e2e_isolated.db`, or `data/prahari_phase18_benchmark.db`. The operational database SHA-256 remained `D270B2882F3A8668081DC2498E3305E7F4255AAED8CA915D40D9560527223FE6`.

| Gate | Fresh result |
|---|---|
| Backend regression/security/provenance | 148 passed |
| Frontend unit | 10 passed in 7 files |
| Production frontend build | Passed; 1,920 modules transformed |
| Playwright | 32 passed across desktop Chromium and Pixel 5 profiles |
| Telemetry benchmark | 1,000/1,000; 0% errors; 37.8 packets/s; p50 24.23 ms; p95 46.73 ms; p99 55.30 ms |
| Copilot benchmark | 100/100; 0% errors; p50 129.20 ms; p95 1,668.20 ms; p99 3,254.03 ms |

The performance figures are local-machine observations, not production capacity or SLO guarantees. Security coverage includes invalid signatures, unknown devices, stale envelopes, nonce and sequence replay (including concurrent duplicate sequences), keyed-device unsigned-ingress denial, signed provenance-conflict rejection, invalid-payload rollback, secret non-disclosure, persisted security events and process-serialized audit-chain verification. Provenance coverage retains strict REAL, EXTERNAL_DATA, MODEL, SIMULATION, REPLAY and PLANNED separation; simulation and replay do not strengthen or mutate REAL state.

An independent final review caused a hardening pass and truthful scope reductions before this final gate: model validation cannot be self-attested, recovery verification is role/artifact constrained, simulated evidence cannot verify recovery, unsupported Copilot claim categories always abstain, DDQI is UNVERIFIED rather than synthesized, disaster-memory storage is not described as immutable, and scenario/chaos APIs are described as manifest persistence rather than execution engines.
