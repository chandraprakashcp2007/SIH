# PRAHARI-NET Software Architecture Specification

**System:** Predictive Resilient Autonomous Hazard & Risk Intelligence Network  
**Competition:** Smart India Hackathon 2026 (SIH26178 / Qualcomm Inc.)  
**Classification:** Disaster Management / Local Edge IoT Command Platform  

---

## 1. System Block Diagram

```
       +-------------------------------------------------------------+
       |                     EDGE SENSOR NODES                       |
       |  +----------------+  +----------------+  +----------------+ |
       |  |    JALA-01     |  |    AGNI-02     |  |    BHUMI-03    | |
       |  | Flood & Surge  |  |  Fire & Smoke  |  | Landslide Tilt | |
       |  +-------+--------+  +-------+--------+  +-------+--------+ |
       +----------|-------------------|-------------------|----------+
                  |                   |                   |
                  +-------------> LoRa RF <---------------+
                           (868 MHz / 433 MHz)
                                      |
                                      v
                        +---------------------------+
                        |   PRAHARI LORA GATEWAY    |
                        | (Serial Bridge/Simulator) |
                        +-------------+-------------+
                                      | HTTP POST (JSON Lines)
                                      v
+-------------------------------------------------------------------------+
|                  LOCAL FASTAPI COMMAND ENGINE (:8000)                   |
|                                                                         |
|  +--------------------+   +--------------------+   +------------------+ |
|  | Telemetry Ingest   |-->| Sensor Trust Engine|-->| Feature Engine   | |
|  | & Gap Validation   |   | (Stuck, Spikes, X) |   | (Velocity, Accel)| |
|  +--------------------+   +--------------------+   +--------+---------+ |
|                                                             |           |
|  +--------------------+   +--------------------+            v           |
|  | Explainability XAI |<--| Hybrid Risk Engine |<--[Isolation Forest]   |
|  | (Human + Machine)  |   | (Multi-Sensor Rule)|   [Anomaly Detector]   |
|  +---------+----------+   +---------+----------+                        |
|            |                        |                                   |
|            v                        v                                   |
|  +--------------------+   +--------------------+   +------------------+ |
|  | Alert Manager      |   | WebSocket Server   |   | SQLite WAL DB    | |
|  | (NDMA CAP Standard)|   | (/ws/live)         |   | (Async Engine)   | |
|  +--------------------+   +---------+----------+   +------------------+ |
+-------------------------------------|-----------------------------------+
                                      | Typed Real-Time Stream
                                      v
+-------------------------------------------------------------------------+
|                  PRAHARI COMMAND CENTRE PWA (:5173)                     |
|                                                                         |
|  - Tactical Geospatial Map (Leaflet with Offline Vector/Grid Fallback)  |
|  - Real-Time Incident Triage Feed & Acknowledge/Resolve Workflow        |
|  - Dedicated Hydrology, Combustion & Inclinometer Dashboards            |
|  - Web Audio API Acoustic Siren Synthesizer (Zero MP3 Dependencies)     |
|  - Offline Operational PRAHARI Copilot Decision Assistant               |
|  - Integrated 14-Scenario Physical Disaster Simulation Board            |
+-------------------------------------------------------------------------+
```

---

## 2. Core Subsystems

### 2.1 Sensor Trust Engine
Traditional IoT networks blindly trust raw ADC readings. PRAHARI calculates an honest dynamic reliability metric ($0 \le \text{Trust} \le 100$) for every sensor based on:
1. **Physical Validity Bounds:** Rejects unrealistic readings (e.g. water level $< 0$ or $> 1000$ cm).
2. **Frozen / Stuck Transducer Check:** Catches analog values with zero micro-variance across 6 consecutive cycles.
3. **Kinematic Jump Check:** Compares instantaneous delta against maximum physically possible rates of change.
4. **Cross-Sensor Contradiction Check:** Dampens single-sensor anomalies (e.g. smoke sensor spiking without heat or flame).

### 2.2 Explainable AI (XAI)
Every alert generates both:
* **Human-Readable Causal Narrative:** Printed in plain operational language for emergency dispatchers.
* **Machine-Readable Factor JSON:** Quantifying exact mathematical weights and raw contributions.

### 2.3 Acoustic Alarm Synthesizer
Built strictly on the browser **Web Audio API**:
* No external audio files to fail or buffer.
* Generates distinct waveforms: dual-tone for floods, high-frequency chirps for fire, low-frequency saw waves for landslides.
* Respects browser autoplay requirements via an explicit **SIREN ARMED** toggle with operator mute support.
