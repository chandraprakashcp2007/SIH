# PRAHARI-NET

**Predictive Resilient Autonomous Hazard & Risk Intelligence Network**  
*SENSE â€¢ PREDICT â€¢ ALERT â€¢ PROTECT*  
Smart India Hackathon 2026 â€” Problem Statement SIH26178

---

## Overview

PRAHARI-NET is a research prototype for local, explainable multi-hazard monitoring. It combines authenticated serial/simulated telemetry, multi-sensor fusion, sensor trust, anomaly detection, causal risk assessment, and local alerts. The current working gateway is Windows/Python; LoRa and a shared Raspberry Pi-class gateway are supported architectural targets, not claimed live deployments.

## Core Hardware Intelligence Nodes

1. **JALA-01 (Flood Intelligence Node):**
   - **Location:** Simulation demo location unless a physical deployment is explicitly configured.
   - **Sensors:** Ultrasonic water level transceiver, tipping-bucket precipitation gauge, DHT22 ambient temperature/humidity.
   - **Metrics:** River level ($cm$), rate of rise ($cm/min$), acceleration ($cm/min^2$), rain intensity ($mm/hr$).
   - **Forecasting:** Polynomial kinematic flood threshold crossing window prediction.

2. **AGNI-02 (Fire & Combustion Intelligence Node):**
   - **Location:** Simulation demo location; ESP32 field node planned.
   - **Sensors:** MQ-2 smoke/flammable gas detector, MQ-135 harmful air quality sensor, narrow-band optical infrared flame sensor, calibrated thermal probe.
   - **Metrics:** Raw ADC combustion signatures, smoke density index, plume growth rate, temperature spike ($^\circ C$).
   - **False Alarm Suppression:** Cross-sensor contradiction checking prevents single-sensor false triggers.

3. **BHUMI-03 (Landslide & Slope Stability Node):**
   - **Location:** Simulation demo location; ESP32 field node planned.
   - **Sensors:** Dual-depth soil-moisture probes, MPU6050 inclinometer, and vibration/geophone sensing are represented by the landslide prototype architecture.
   - **Metrics:** Soil saturation, tilt delta, vibration RMS, and rainfall context.
   - **Status:** Existing landslide risk engine available; field ESP32 deployment remains planned unless physically connected.

4. **VAYU-04 (Air Intelligence):**
   - **Status:** Planned only.
   - No live physical PM2.5, PM10, CO, VOC, or toxic-gas telemetry is claimed unless an appropriate physical sensor or trusted external source is configured.

5. **AKASHA-05 (Atmospheric Intelligence):**
   - **Status:** Planned only.
   - External meteorological and oceanographic integration is not yet configured.
   - No live satellite, cyclone, wind, rainfall, or ocean observation is claimed until a real provider/import source is connected.

## Authoritative Risk & Safety Architecture

The authoritative hazard calculation pipeline is:
$$\text{Sensors} \rightarrow \text{Feature Extraction} \rightarrow \text{Sensor Trust} \rightarrow \text{Multi-Sensor Fusion} \rightarrow \text{Hybrid Risk Engine} \rightarrow \text{Alert Service}$$

**PRAHARI COPILOT** sits strictly above this layer as an operational decision-support tool. It has **read-only** visibility and **never modifies** hazard scores, never silences active alarms, and never fabricates telemetry.

## Run locally

```powershell
.\scripts\bootstrap.ps1
.\scripts\start-dev.ps1
```

- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/api/docs

The checked-in `.env` enables `DEV_AUTH_BYPASS=true` for the local SIH demo, so any non-empty credentials work. The login screen displays this mode. Set `DEV_AUTH_BYPASS=false`, replace `SECRET_KEY`, and configure `CORS_ORIGINS` before a production deployment; standard database-backed password verification then remains in force.

Run verification with:

```powershell
.\scripts\run-tests.ps1
Set-Location frontend
npm run test:e2e
```

