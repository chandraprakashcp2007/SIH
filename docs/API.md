# PRAHARI-NET REST & WebSocket API Reference

**Base URL:** `http://127.0.0.1:8000/api`  
**WebSocket URL:** `ws://127.0.0.1:8000/ws/live`  
**Interactive Swagger Documentation:** `http://127.0.0.1:8000/api/docs`  

---

## 1. Authentication (`/api/auth`)

### `POST /api/auth/login`
Authenticates an operator and issues an HS256 JWT access token.
* **Request:**
```json
{
  "username": "operator",
  "password": "prahari2026!"
}
```
* **Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "username": "operator",
    "role": "OPERATOR"
  }
}
```

---

## 2. Telemetry Ingestion (`/api/telemetry`)

### `POST /api/telemetry/ingest`
High-throughput ingestion endpoint for real LoRa hardware or simulation bridge.
* **Request Body:**
```json
{
  "version": 1,
  "node_id": "JALA-01",
  "sequence": 412,
  "timestamp": "2026-09-09T20:00:00+05:30",
  "metrics": {
    "water_level_cm": 54.2,
    "water_rise_rate_cm_min": 1.25,
    "rain_intensity": 12.4,
    "temperature_c": 29.1,
    "humidity_pct": 76.0
  },
  "rssi": -78,
  "battery_pct": 91.0,
  "is_simulation": false
}
```
* **Response (200 OK):**
```json
{
  "status": "success",
  "node_id": "JALA-01",
  "sequence": 412,
  "risk_score": 38.5,
  "risk_band": "WATCH",
  "alerts_generated": 1,
  "sensor_trust": {
    "water_level_sensor": 98.0,
    "rain_sensor": 95.0
  }
}
```

---

## 3. Incident Alerts (`/api/alerts`)

### `GET /api/alerts`
Query active or historical disaster alerts. Query params: `state`, `severity`, `node_id`, `limit`.

### `POST /api/alerts/{id}/acknowledge`
Operator acknowledgement.
* **Request:** `{"notes": "Field ranger notified"}`

### `POST /api/alerts/{id}/resolve`
Operator resolution.
* **Request:** `{"resolution_notes": "Culvert blockage cleared. Water levels returned to normal."}`

---

## 4. Simulator Engine (`/api/simulator`)

### `GET /api/simulator/scenarios`
Lists all 14 available physical disaster scenarios.

### `POST /api/simulator/scenario/{name}`
Engages a scenario:
`ALL_NORMAL`, `FLOOD_RAMP`, `FLASH_FLOOD`, `FIRE_DEVELOPMENT`, `FALSE_SMOKE_SENSOR_SPIKE`, `CONFIRMED_FIRE`, `LANDSLIDE_SATURATION`, `LANDSLIDE_MOVEMENT`, `SENSOR_FAILURE`, `NODE_OFFLINE`, `PACKET_LOSS`, `INTERNET_OUTAGE`, `RECOVERY`, `RESET`.

---

## 5. WebSocket Protocol (`/ws/live`)

Clients receive real-time JSON frames:
```json
{
  "type": "telemetry.updated",
  "data": {
    "node_id": "JALA-01",
    "sequence": 413,
    "metrics": { "water_level_cm": 55.4 }
  }
}
```
Supported event types:
* `telemetry.updated`
* `node.status_changed`
* `risk.updated`
* `alert.created`
* `alert.acknowledged`
* `alert.resolved`
* `simulation.updated`
