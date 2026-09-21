# PRAHARI-NET: Operational Research Notes & Design Principles

**Author:** Technical Architecture & UX Team  
**Date:** September 2026  
**Context:** Smart India Hackathon 2026 — Problem Statement SIH26178 (Qualcomm Inc.)  
**Scope:** Verified operational principles extracted from public platforms: NDMA SACHET, NASA FIRMS, and industrial Emergency Operation Centres (EOC).

---

## 1. Verified Public Disaster Alert & Monitoring Platforms

### 1.1 NDMA SACHET (India National Disaster Alert Portal)
*Developed by C-DOT for the National Disaster Management Authority (NDMA), Government of India.*

* **Core Protocol:** Implements the international **Common Alerting Protocol (CAP v1.2)** standard XML format. Alerts are structured with standardized fields: `Identifier`, `Sender`, `SentTime`, `Status`, `MsgType`, `Scope`, `Category`, `Urgency`, `Severity`, `Certainty`, `Headline`, `Description`, `Instruction`, and `Area` (geocodes/polygons).
* **Multi-Agency Ingestion:** Synthesizes warnings from primary Indian technical agencies:
  * India Meteorological Department (IMD) — Cyclones, heavy rain, heatwaves.
  * Central Water Commission (CWC) — River level, flood hydrographs.
  * Indian National Centre for Ocean Information Services (INCOIS) — Tsunami, storm surges.
  * Geological Survey of India (GSI) — Landslide warnings.
  * Forest Survey of India (FSI) — Forest fire risk.
* **Resilient Internet-Independent Dissemination:** Utilizes **Cell Broadcast (CB)** alongside SMS, web portal, and coastal sirens. Cell Broadcast transmits directly across radio cell towers without needing individual device telephone numbers or internet data connectivity, operating during severe network congestion and telecommunication cable cuts.
* **The "3A" Operational Model:**
  1. *Alert:* Timely, unambiguous notice of impending threat.
  2. *Awareness:* Contextual educational guidance ("Do's & Don'ts").
  3. *Action:* Explicit, immediate protocols for local authorities and residents.
* **Key Design Takeaway for PRAHARI-NET:** Strict separation between raw sensor observation and actionable alert; geo-targeted scoping; resilience against local internet failure via direct RF/LoRa broadcasting.

---

### 1.2 NASA FIRMS (Fire Information for Resource Management System)
*Operated by NASA Earthdata / LANCE (Land, Atmosphere Near real-time Capability for EOS).*

* **Sensors & Revisit Rates:** Uses MODIS (Terra/Aqua, 1 km) and VIIRS (Suomi-NPP/NOAA-20/NOAA-21, 375 m) sensor payloads to provide Near Real-Time (NRT) active thermal anomaly detections within 3 hours of overpass.
* **Confidence & Anomaly Scoring:** Thermal detections do not simply output binary "fire / no fire". Detections provide explicit detection confidence ratings (0–100% or nominal/low/high) based on background thermal contrast, false-positive filtering (e.g. gas flaring, static industrial hot spots), and solar reflection angles.
* **Multi-Layer Geospatial Context:** FIRMS maps overlay thermal points against contextual environmental layers: smoke/aerosol index, land cover classification, settlements, and precipitation records.
* **Key Design Takeaway for PRAHARI-NET:** Never rely on single-sensor triggers. High gas/smoke alone must not trigger high fire risk without thermal/flame corroboration or trust validation. Display explicit confidence metrics alongside risk values.

---

### 1.3 Industrial & Municipal Emergency Operation Centres (EOC)
*Reference patterns from civil protection centres, offshore SCADA, and utility dispatch consoles.*

* **Information Hierarchy:**
  * **Level 1 (Glanceable Health Strip):** System connectivity, time synchronization, node fleet status (e.g., "3/3 Nodes Online"), active critical alarms.
  * **Level 2 (Geospatial Tactical Map):** Spatially grounded overview with semantic symbology (green = normal, yellow = watch, orange = warning, red = critical, grey = offline).
  * **Level 3 (Actionable Incident Queue):** Chronological triage stream showing severity, elapsed time, confidence, and unacknowledged states.
  * **Level 4 (Telemetry & Node Drilldown):** Technical metrics, rate of change (first derivative), and sensor health.
* **Acoustic Restraint:** Sirens must be semantically differentiated. Autoplay must be explicitly opted-in. Auditory alarms must allow operator mute once acknowledged.
* **Explainability Requirement:** Automated alerts must present operator-facing causality ("WHY did this alarm trigger?"). Black-box alerts lead to operator alert fatigue and distrust.

---

## 2. Synthesized Design Principles for PRAHARI-NET

1. **Map-First Tactical Center:** Central interactive map anchored with geo-referenced nodes, instant visual status reflection, and offline vector/grid fallback if internet tile servers are unreachable.
2. **Restrained Professional Command-Centre Aesthetic:** High-contrast dark theme (`#07111F` to `#14273C`), monospace values for sensor metrics, and color reserved strictly for operational severity.
3. **Sensor Trust as a First-Class Citizen:** Track sensor reliability (0–100%) to catch sensor drift, frozen values, and contradictory spikes before feeding raw numbers into risk algorithms.
4. **Transparent Hybrid AI:** Multi-sensor rule fusion paired with lightweight unsupervised anomaly detection (Isolation Forest). Honest labeling of model sources (`RULE_FUSION`, `ANOMALY_MODEL`, `SIMULATION`).
5. **Human-in-the-Loop & Auditing:** Incident lifecycle transitions (`NEW` → `ACKNOWLEDGED` → `MONITORING` → `RESOLVED`) with immutable operator audit logging.
6. **Local Edge Sovereignty:** Fully autonomous local execution on standard field laptops without requiring external cloud connectivity.
