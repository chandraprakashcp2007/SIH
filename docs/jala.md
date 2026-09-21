# JALA-01 Flood Intelligence Node Specification

**Node Identifier:** JALA-01  
**Hazard Domain:** River Hydrodynamics, Flash Flooding & Surge Forecasting  
**Deployment Zone:** Brahmaputra Basin - Sector 4 (Guwahati, Assam)  
**Coordinates:** Latitude 26.1850° N, Longitude 91.7539° E (Elevation 55m)  

## Physical Transducers
1. **Ultrasonic Range Transceiver (AJ-SR04M Waterproof):** Measures distance to river water surface with $\pm 2mm$ precision.
2. **Tipping-Bucket Rain Gauge:** 0.2mm resolution rain collector measuring instantaneous precipitation rate ($mm/hr$).
3. **DHT22 Temperature & Humidity:** Ambient atmospheric sensors for sound velocity temperature compensation.

## Hydrological Thresholds
- **Nominal River Baseline:** $30.0 - 50.0\text{ cm}$
- **Watch Threshold:** $60.0\text{ cm}$ (or rise rate $> 2.0\text{ cm/min}$)
- **Warning Threshold:** $120.0\text{ cm}$ (or rise rate $> 4.0\text{ cm/min}$)
- **Critical Danger Datum:** $180.0\text{ cm}$ (or flash flood surge rate $> 6.0\text{ cm/min}$)

## Kinematic Surge Forecasting
The prediction engine models water elevation using 2nd-order Taylor series expansion:
$$h(t + \Delta t) = h_0 + v_0 \cdot \Delta t + \frac{1}{2} a \cdot (\Delta t)^2$$
Where $v_0$ is water rise velocity ($cm/min$) and $a$ is surge acceleration ($cm/min^2$). The engine projects the exact threshold crossing time window (e.g. "ESTIMATED 8-12 MINUTES").
