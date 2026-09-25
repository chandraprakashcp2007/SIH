# PRAHARI-NET Provenance Contract

Every observation uses one canonical `source_mode` value. The legacy `is_simulation` field remains accepted during migration, but new producers should send `source_mode`.

| Mode | Meaning | May update live node state? |
|---|---|---|
| `REAL` | Packet from physically connected and verified hardware | Yes |
| `SIMULATION` | Software-generated demonstration telemetry | Yes, unless protected REAL state exists |
| `EXTERNAL_DATA` | Government, satellite, or other authoritative observation | No; it belongs in the later external-observation path |
| `REPLAY` | Historical playback used for analysis or demonstrations | No; stored in isolation |
| `PLANNED` | Architecture or hardware not yet connected | No telemetry permitted |

The ingestion service records device time, server receipt time, clock drift, transport, gateway identifier, sequence, and provenance. It quarantines invalid, stale, future, out-of-order, planned-node, and provenance-conflicting packets with explicit reason codes. Duplicate suppression remains backward compatible.

## Current truthful state

- The supported physical prototype path is NodeMCU ESP8266 → USB Serial → Windows Python gateway.
- A packet is `REAL` only while that physical workflow is connected and verified.
- Default seeded telemetry and locations are `SIMULATION`; demo coordinates are not field-deployment claims.
- VAYU-04 and AKASHA-05 are `PLANNED` and have no seeded telemetry, risk, confidence, or online status.
- No government or satellite source is currently connected, so no observation is claimed as `EXTERNAL_DATA`.
- `REPLAY` is supported as isolated provenance; it never changes current live state.

SQLite schema evolution runs safely during backend startup and adds missing columns without deleting data. PostgreSQL deployments should apply equivalent managed migrations before rollout.
