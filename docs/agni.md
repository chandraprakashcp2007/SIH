# AGNI-02 Fire & Atmospheric Combustion Node Specification

**Node Identifier:** AGNI-02  
**Hazard Domain:** Wildfire Kinetics, Atmospheric Combustion & Plume AI  
**Deployment Zone:** Similipal Forest Perimeter - Ridge A (Mayurbhanj, Odisha)  
**Coordinates:** Latitude 21.8485° N, Longitude 86.4250° E (Elevation 420m)  

## Physical Transducers
1. **MQ-2 Metal Oxide Gas Sensor:** Detects methane, propane, smoke aerosols, and combustible hydrocarbons ($100 - 10,000\text{ ppm}$).
2. **MQ-135 Air Quality Sensor:** Monitors carbon dioxide ($CO_2$), nitrogen oxides ($NO_x$), and ammonia ($NH_3$) for broad atmospheric smoke validation.
3. **Narrow-Band Infrared Optical Flame Detector (760 - 1100 nm):** Photodiode detecting radiation from active combustion.
4. **Calibrated Waterproof Thermal Probe (DS18B20):** Measures ambient heat spikes ($^\circ C$).

## False Alarm Prevention via Sensor Trust
Single-sensor gas spikes (e.g. insect ingress or alcohol evaporation) frequently cause false alarms in legacy systems. AGNI-02 requires cross-sensor corroboration:
- If MQ-2 spikes to 850 ADC, but temperature is $27^\circ C$, flame is False, and MQ-135 is nominal, the **Sensor Trust Engine** discounts MQ-2 reliability to $30\%$ and flags `SENSOR_CONTRADICTION`.
- The risk score is capped at WATCH/NORMAL ($< 50\%$), preventing false emergency evacuations.
- When thermal rise, flame detection, and smoke rise simultaneously, confidence exceeds $95\%$ and CRITICAL alerts dispatch immediately.
