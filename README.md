# PRAHARI-NET

**Predictive Resilient Autonomous Hazard & Risk Intelligence Network**  
*SENSE • PREDICT • ALERT • PROTECT*  
Smart India Hackathon 2026 — Problem Statement SIH26178

---

## Overview

PRAHARI-NET is an autonomous disaster intelligence and early warning command system designed for deployment in remote, disaster-prone sectors across India. Operating completely independent of public cloud and internet infrastructure, PRAHARI combines long-range LoRa RF telemetry, multi-sensor kinematic fusion, dynamic transducer trust verification, unsupervised anomaly detection (Isolation Forest), explainable causal risk assessment, and auditory alarm synthesis.

## Core Hardware Intelligence Nodes

1. **JALA-01 (Flood Intelligence Node):**
   - **Location:** Brahmaputra Basin - Sector 4 (Assam)
   - **Sensors:** Ultrasonic water level transceiver, tipping-bucket precipitation gauge, DHT22 ambient temperature/humidity.
   - **Metrics:** River level ($cm$), rate of rise ($cm/min$), acceleration ($cm/min^2$), rain intensity ($mm/hr$).
   - **Forecasting:** Polynomial kinematic flood threshold crossing window prediction.

2. **AGNI-02 (Fire & Combustion Intelligence Node):**
   - **Location:** Similipal Forest Perimeter - Ridge A (Odisha)
   - **Sensors:** MQ-2 smoke/flammable gas detector, MQ-135 harmful air quality sensor, narrow-band optical infrared flame sensor, calibrated thermal probe.
   - **Metrics:** Raw ADC combustion signatures, smoke density index, plume growth rate, temperature spike ($^\circ C$).
   - **False Alarm Suppression:** Cross-sensor contradiction checking prevents single-sensor false triggers.

3. **BHUMI-03 (Landslide & Slope Stability Node):**
   - **Location:** NH-58 Ghat Section Km 42 (Uttarakhand)
   - **Sensors:** Dual-depth Total Water Soil (TWS) capacitance probes, MPU6050 6-axis MEMS inclinometer, piezoelectric geophone micro-seismic transducer.
   - **Metrics:** Upper/lower soil saturation ($%$), angular shear tilt delta ($\Delta ^\circ$), vibration RMS velocity ($mm/s$).

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
