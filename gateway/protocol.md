# PRAHARI-NET LoRa / Serial Gateway Protocol Specification

**Standard Version:** 1.0  
**RF Frequency:** 868.1 MHz / 433 MHz ISM Band  
**Modulation:** LoRa Chirp Spread Spectrum (CSS)  
**Spreading Factor (SF):** SF7 / SF8  
**Bandwidth:** 125 kHz  
**Coding Rate:** 4/5  
**Physical Interface:** USB-to-UART bridge (CP2102 / CH340 / FTDI) at 115200 baud, 8N1  

---

## 1. Frame Architecture

The PRAHARI gateway receives newline-delimited (`\n`) JSON frames emitted by the configured gateway transport. USB serial is the verified prototype path; LoRa is an optional field transport when physically integrated.

### 1.1 JSON Packet Schema
```json
{
  "version": 1,
  "node_id": "JALA-01",
  "sequence": 412,
  "timestamp": "2026-09-09T20:00:00+05:30",
  "metrics": {
    "water_level_cm": 54.2,
    "water_distance_cm": 145.8,
    "water_rise_rate_cm_min": 1.25,
    "water_rise_acceleration": 0.04,
    "rain_intensity": 12.4,
    "temperature_c": 29.1,
    "humidity_pct": 76.0
  },
  "rssi": -78,
  "battery_pct": 91.0
}
```

---

## 2. Field Definitions

| Field | Type | Required | Units / Range | Description |
|---|---|---|---|---|
| `version` | Integer | Yes | `1` | Protocol revision schema |
| `node_id` | String | Yes | `JALA-01`, `AGNI-02`, `BHUMI-03`, `VAYU-04`, `AKASHA-05` | Unique node identifier |
| `sequence` | Integer | Yes | `0` to `4,294,967,295` | Monotonic 32-bit packet counter |
| `timestamp` | String | Optional | ISO-8601 | Local GPS/RTC timestamp |
| `rssi` | Integer | Yes | `-130` to `-20` dBm | Received Signal Strength Indication |
| `battery_pct` | Float | Yes | `0.0` to `100.0` % | Estimated remaining battery charge |
| `metrics` | Object | Yes | Key-value pairs | Node-specific physical sensor telemetry |

---

## 3. Node-Specific Metrics Specification

### JALA-01 (Flood Intelligence)
* `water_level_cm` (Float): Calibrated river/channel water level from bed datum.
* `water_distance_cm` (Float): Raw ultrasonic/radar time-of-flight distance.
* `water_rise_rate_cm_min` (Float): Computed rate of rise over 60 seconds.
* `water_rise_acceleration` (Float): Rate of change of velocity (surge acceleration).
* `rain_intensity` (Float): Tipping bucket or optical disdrometer rain intensity in mm/hr.
* `temperature_c` (Float): Ambient atmospheric temperature in Celsius.
* `humidity_pct` (Float): Relative humidity percentage.

### AGNI-02 (Fire & Environmental Intelligence)
* `mq2_raw` (Float): Raw analog ADC reading from MQ-2 combustible gas/smoke sensor (0–1024).
* `mq135_raw` (Float): Raw analog ADC reading from MQ-135 air quality / hazardous gas sensor.
* `smoke_index` (Float): Calibrated smoke density index.
* `gas_index` (Float): Calibrated harmful gas index.
* `temperature_c` (Float): High-precision thermal sensor reading in Celsius.
* `humidity_pct` (Float): Relative ambient humidity.
* `flame_detected` (Boolean): Digital IR photodiode flame sensor state.
* `camera_fire_confidence` (Float): Vision edge inference confidence (0.0 to 1.0).

### BHUMI-03 (Landslide & Slope Stability)
* `soil_moisture_upper_pct` (Float): Volumetric water content at 15 cm depth (0–100%).
* `soil_moisture_lower_pct` (Float): Volumetric water content at 60 cm depth (0–100%).
* `tilt_x_deg` (Float): Inclinometer X-axis tilt in degrees.
* `tilt_y_deg` (Float): Inclinometer Y-axis tilt in degrees.
* `tilt_delta_deg` (Float): Euclidean vector displacement from geological zero baseline.
* `vibration_level` (Float): Instantaneous piezoelectric vibration sensor amplitude.
* `vibration_rms` (Float): Root-Mean-Square vibration over 2-second integration window.
* `rain_context` (Float): Cumulative antecedent precipitation over past 24 hours.

---

## 4. Error Handling & Integrity Verification

1. **CRC / Framing Check:** Serial line feeds require valid JSON strings. Incomplete chunks are buffered until `\n`.
2. **Sequence Gap Tracking:** Gateway records sequence discontinuities to compute packet loss percentage.
3. **Duplicate Filter:** Packets matching the immediately previous sequence number on the same node are flagged as duplicates and filtered.
