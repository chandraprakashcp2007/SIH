# PRAHARI-NET Project Overview

**Competition:** Smart India Hackathon 2026 (SIH26178)  
**Product:** PRAHARI-NET (Predictive Resilient Autonomous Hazard & Risk Intelligence Network)  
**Tagline:** SENSE • PREDICT • ALERT • PROTECT  

## Problem Context & Motivation

Critical disaster scenarios (such as Himalayan flash floods, Eastern Ghats wildfires, and monsoon slope landslides) frequently destroy local cellular telecommunications and fiber backhauls at the exact moment early warnings are needed. Commercial IoT platforms depend heavily on AWS/Azure cloud ingestion, failing instantly when external WAN disconnects.

PRAHARI-NET solves this through complete **Local Edge Sovereignty**:
- The field nodes transmit compact encrypted telemetry packets over 868MHz / 433MHz LoRa.
- A rugged field gateway forwards packets to a local command workstation running FastAPI and SQLite WAL.
- The entire feature extraction, sensor trust discounting, anomaly scoring, multi-sensor fusion, and causal explainability pipeline runs locally without internet.
- **PRAHARI COPILOT** provides emergency operators with grounded answers, unacknowledged alarm summaries, and causal explanations in sub-250ms latency.
