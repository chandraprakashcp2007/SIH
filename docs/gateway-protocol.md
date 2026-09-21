# PRAHARI Gateway & LoRa Communication Protocol

## Frame Format

PRAHARI nodes transmit telemetry using compact JSON Lines over LoRa RF (868MHz / 433MHz):

```json
{
  "version": 1,
  "node_id": "JALA-01",
  "sequence": 501,
  "timestamp": "2026-09-09T22:30:00+05:30",
  "metrics": {
    "water_level_cm": 42.5,
    "water_distance_cm": 157.5,
    "water_rise_rate_cm_min": 0.2,
    "water_rise_acceleration": 0.01,
    "rain_intensity": 2.0,
    "temperature_c": 28.5
  },
  "rssi": -74,
  "battery_pct": 93.5,
  "is_simulation": false
}
```

## Protocol Attributes
- **Baud Rate:** 115200 baud UART USB Serial interface.
- **Sequence Gap Detection:** The gateway tracks monotonically increasing sequence counters per node. If sequence jumps from 101 to 104, 2 lost packets are recorded immediately.
- **Duplicate Suppression:** Duplicate sequence numbers received within a 10-second window are flagged and deduplicated.
- **Signal Quality Metric:** Real-time RSSI ($dBm$) and SNR monitoring flags antenna misalignments before data loss occurs.
