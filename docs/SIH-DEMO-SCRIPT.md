# PRAHARI-NET: 5-Minute Official SIH 2026 Jury Demo Script

**Competition:** Smart India Hackathon 2026  
**Problem Statement:** SIH26178 (Qualcomm Inc. / Hardware / Disaster Management)  
**Target Jury Route:** `http://localhost:5173/demo`  

---

## Chronological Demo Timeline (00:00 – 05:00)

### [00:00 – 00:45] Minute 1: Problem Identity & Edge Sovereignty
1. **Introduction:**  
   *"Respected jury members, in environmental disasters across India—from Assam flash floods to Uttarakhand landslides and Odisha forest fires—reactive disaster response arrives too late. Furthermore, cellular towers and internet cables are often the very first infrastructure severed during extreme weather. We present **PRAHARI-NET** (Predictive Resilient Autonomous Hazard & Risk Intelligence Network)."*
2. **Key Metric:** Point out the top bar: **"LOCAL EDGE MODE"**, **"LoRa SX1276 Healthy"**, **"3/3 Nodes Online"**. Emphasize that the entire system—sensing, LoRa packet ingestion, hybrid physical AI, WebSocket stream, and command dashboard—operates 100% locally on this field laptop without requiring internet access.

### [00:45 – 01:45] Minute 2: JALA-01 Flood Escalation & Prediction
1. **Action:** On `/demo`, click Step 2 (**FLOOD RAMP**) then Step 3 (**FLASH FLOOD**).
2. **Observe in UI:**
   * Water level rises from 34.2 cm → 75 cm (Normal → Watch).
   * Accelerates over 180 cm with torrential 115 mm/hr rainfall.
   * Status transitions: **Watch → Warning → Critical Flood**.
   * **Auditory Siren:** The dual-tone critical flood siren sounds.
   * **Explainable AI (WHY?):** Click the JALA card to show: *"Water rose to 210cm. Rate of rise increased to 7.5 cm/min. Positive surge acceleration detected."*
   * **Honest Prediction Window:** Shows breach estimated in **~12–16 minutes**, not unrealistic decimals.
3. **Mitigate:** Click **Acknowledge** in the Right Rail. Show incident state moving to `ACKNOWLEDGED`.

### [01:45 – 02:45] Minute 3: Sensor Trust Innovation (False Smoke Spike vs Confirmed Fire)
1. **The Problem:** Single gas sensors frequently spike due to humidity or insect interference, causing panic false alarms in traditional IoT systems.
2. **Action:** Click Step 5 (**FALSE_SMOKE_SENSOR_SPIKE**).
3. **Observe in UI:**
   * MQ-2 smoke sensor spikes to 850 ADC.
   * But ambient temperature is 27.2°C, optical flame is CLEAR, and MQ-135 is normal.
   * **Sensor Trust Engine Action:** The system drops MQ-2 trust to 25%, flags a sensor contradiction anomaly, and keeps AGNI at **WATCH**, completely suppressing a false critical siren!
4. **Action:** Now click Step 6 (**FIRE_DEVELOPMENT**).
5. **Observe in UI:**
   * Thermal surge (>68°C), optical flame detected, and visual AI confidence rises.
   * Multi-sensor fusion corroborates; system immediately triggers **CRITICAL FIRE** with high-frequency rapid pulsing alarm.

### [02:45 – 03:45] Minute 4: BHUMI-03 Landslide Dynamics & Ground Shear
1. **Action:** Click Step 8 (**LANDSLIDE_SATURATION**) then Step 9 (**LANDSLIDE_MOVEMENT**).
2. **Observe in UI:**
   * Antecedent rain accumulates to 95 mm; dual-layer soil moisture reaches 92% pore-water saturation.
   * Inclinometer detects structural tilt delta of 4.8° accompanied by 14.2g vibration RMS micro-tremors.
   * Fused geotechnical score exceeds 85% (**CRITICAL LANDSLIDE**).
   * Low-frequency rumble siren sounds; recommended operational action states: *"Trigger road closure on NH-58; sound hillside evacuation siren."*

### [03:45 – 04:30] Minute 5: Physical LoRa Hardware & Real Serial Demonstration
1. **Explain Hardware Architecture:** Show the SX1276 transceiver and ESP32 gateway.
2. **Show Gateway Ingestion:** Point out the Network page (`/network`) with live packet sequences, RSSI signal indicators, sequence gap counters, and CRC verification.
3. **Explain Physical Buzzer Integration:** Show the gateway commands ready for field sirens (`BUZZER_CRITICAL_FLOOD`, `BUZZER_CRITICAL_FIRE`, etc.).

### [04:30 – 05:00] Wrap-up & Q&A Readiness
1. Open **PRAHARI Copilot** in the bottom-right.
2. Ask: *"Why was this fire alert generated?"* or *"Which sensors have low trust?"*
3. Copilot provides immediate grounded, non-hallucinated explanations directly from the local database.
4. Click **Reset All to Nominal**; show full recovery.
