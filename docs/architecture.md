# PRAHARI-NET Architecture Specification

## Pipeline Flow

1. **Sensors:** Field instruments collect analog/digital measurements (Ultrasonic, Rain Gauge, MQ-2, MQ-135, MPU6050, Geophone).
2. **ESP32 Node Firmware:** Packages measurements into JSON/binary frames with sequence counters, battery voltage, and RSSI.
3. **LoRa RF Link:** Transmits across 868MHz/433MHz unlicensed ISM bands up to 15km line-of-sight.
4. **PRAHARI Gateway:** Receives RF packets over USB serial UART (`pyserial`) or internal physics simulator.
5. **Telemetry Validation:** Ingests packets, detects sequence drops, identifies duplicates, and measures packet delivery rates.
6. **Feature Engine:** Computes 1st derivatives (velocity/rise rate) and 2nd derivatives (acceleration).
7. **Sensor Trust Engine:** Dynamically rates transducer honesty ($0-100\%$) based on physical validity bounds, stuck sensor checks, kinematic jump tests, and cross-sensor contradiction checks.
8. **Multi-Sensor Fusion:** Trust-weighted heuristic rules combine corroborating indicators while suppressing isolated glitches.
9. **Hybrid Risk Engine:** Produces authoritative 0–100 calibrated risk scores, categorizing into NORMAL, WATCH, WARNING, and CRITICAL.
10. **Explainability Engine (XAI):** Generates both human-readable causal text and machine-readable factor JSON.
11. **Alert Service:** Enforces NDMA CAP alert lifecycle: NEW, ACKNOWLEDGED, MONITORING, RESOLVED.
12. **Command Centre & WebSocket:** Real-time push stream over `/ws/live` to React PWA.
13. **PRAHARI COPILOT:** Operational assistant providing grounded explanations and fast-path responses.
