# PRAHARI-NET Safety Boundaries & Operational Limitations

## Engineering Prototype Disclaimers

1. **Advisory Decision Support:** PRAHARI-NET is an engineering prototype developed for Smart India Hackathon 2026 (Problem Statement SIH26178). It provides auxiliary decision-support intelligence to certified emergency dispatchers and does not supersede official NDMA, IMD, or CWC disaster warnings.
2. **Copilot Read-Only Guarantee:** PRAHARI COPILOT operates strictly above the operational layer with read-only database permissions. It cannot modify hazard scores, lower warning bands, acknowledge alerts without operator action, or silence audible sirens.
3. **Anti-Hallucination Policy:** If visual AI streams, thermal sensors, or rain gauges are offline, Copilot is explicitly constrained to state: *"Current data is unavailable"* rather than generating fictitious confidence scores.
4. **Data Mode Transparency:** All inquiries clearly separate `SIMULATION` data from `REAL` hardware RF packets.
