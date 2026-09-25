# Pancha Bhootha Architecture

PRAHARI-NET exposes a central domain registry through `GET /api/elements`. The registry defines identity and capability; it does not fabricate observations.

| Domain | Element | Current source | Hardware state | Risk engine |
|---|---|---|---|---|
| JALA-01 | WATER | SIMULATION by default; REAL accepted from verified serial hardware | ESP8266 bench prototype available | Available |
| AGNI-02 | FIRE | SIMULATION | ESP32 field node planned | Available |
| BHUMI-03 | EARTH | SIMULATION | ESP32 field node planned | Available |
| VAYU-04 | AIR | PLANNED | Planned | Not implemented |
| AKASHA-05 | ATMOSPHERE | PLANNED | Planned; external meteorological integration pending | Not implemented |

The existing JALA, AGNI, and BHUMI engines remain unchanged. Unknown or planned domains fail safely and are never routed through a fallback authoritative risk calculation. VAYU and AKASHA appear in the dashboard only as truthful capability cards with no sensor readings or risk percentages.

Each definition includes its primary hazards, supported metric names, default provenance, hardware state, risk-engine availability, description, and hardware profile. This registry replaces new node-ID conditionals while legacy code is migrated incrementally.
