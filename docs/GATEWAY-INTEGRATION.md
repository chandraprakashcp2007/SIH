# PRAHARI-NET Hardware LoRa & USB Gateway Integration Guide

**Target Hardware:** Semtech SX1276 / SX1262 LoRa Transceiver + ESP32 / Arduino Nano  
**RF Frequency:** 868.1 MHz (IN865 Band for India) or 433 MHz ISM  
**Physical Interface:** USB-to-UART Serial (CP2102 / CH340) at 115200 Baud  

---

## 1. Hardware Connection

Connect the LoRa Gateway Concentrator module to the laptop USB port.  
On Windows, check Device Manager for the COM port (e.g. `COM3` or `COM4`).

### Environment Configuration (`.env`)
```env
SERIAL_PORT=COM3
SERIAL_BAUD_RATE=115200
GATEWAY_MODE=REAL
```

---

## 2. Running Real Hardware Serial Mode

Run the gateway serial bridge script:
```powershell
python gateway/serial_bridge.py
```
The script will:
1. Open the specified serial port.
2. Read newline-delimited JSON packets.
3. Validate protocol checksums and sequence counters.
4. Forward validated packets via HTTP POST to `http://127.0.0.1:8000/api/telemetry/ingest`.

---

## 3. Physical Gateway Buzzer Command Abstraction

When operating a physical siren or buzzer on the gateway microcontroller, the gateway supports receiving command lines over serial:
* `BUZZER_WATCH` — 3 short beeps
* `BUZZER_WARNING` — Repeated moderate beeps
* `BUZZER_CRITICAL_FIRE` — Rapid high-frequency emergency pulsing
* `BUZZER_CRITICAL_FLOOD` — Alternating dual-tone alarm
* `BUZZER_CRITICAL_LANDSLIDE` — Low-frequency repeating saw tone
* `BUZZER_OFF` — Silence buzzer upon operator acknowledgement
