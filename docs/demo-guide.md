# PRAHARI-NET SIH Judge Demonstration Guide

## Step-by-Step SIH 2026 Live Demo Script

### 1. Baseline Nominal State
- Open Command Centre at `http://localhost:5173`.
- Observe the five Pancha Bhootha software domains: JALA-01 (Flood), AGNI-02 (Fire), BHUMI-03 (Landslide), VAYU-04 (Air), and AKASHA-05 (Atmosphere).
- Click floating Copilot trigger (bottom-right).
- Type: `How is the system?`
- **Expected:** Copilot responds in $< 150ms$: all nodes nominal, 0 active alarms, Local Edge armed.

### 2. Flood Ramp Scenario & Causal Explainability
- In Simulator Board, click **FLOOD RAMP**.
- Watch Brahmaputra hydrograph climb in real time over WebSocket.
- Once warning/critical alert triggers, ask Copilot:
  `Why is JALA critical?`
- **Expected:** Copilot outputs exact water level ($cm$), rate of rise ($+cm/min$), rain intensity, and explains the 2nd-order surge acceleration.

### 3. False Alarm Prevention Demonstration (Core Innovation)
- Trigger **FALSE SMOKE SENSOR SPIKE** on AGNI-02.
- MQ-2 spikes violently to 850 ADC, but temperature remains $27^\circ C$, flame is False, MQ-135 is normal.
- Ask Copilot: `Which sensor currently has low trust?`
- **Expected:** Copilot identifies AGNI-02 MQ-2 smoke sensor at 30% trust with `SENSOR_CONTRADICTION`. Explains that the risk engine discounted it, preventing a false critical alarm.

### 4. WAN Internet Severed (Offline Local Edge Demonstration)
- Disconnect internet or click **INTERNET OUTAGE** scenario.
- Copilot status indicator dynamically transitions: `ONLINE AI` $\rightarrow$ `LOCAL ASSISTANT`.
- Ask: `Is the gateway connected?` or `Which node has highest risk?`
- **Expected:** Copilot continues functioning with 100% accuracy from the local backend without freezing or throwing errors.
