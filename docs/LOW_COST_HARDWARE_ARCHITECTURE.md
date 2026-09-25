# Low-Cost Hardware Architecture

PRAHARI-NET intentionally uses cheap distributed sensor controllers and one shared edge computer:

```text
ESP8266 / ESP32 field nodes
        ↓ USB Serial / Wi-Fi / planned LoRa
one shared Windows or Raspberry Pi-class gateway
        ↓
local and central PRAHARI services
```

## Current prototype

- Node controller: NodeMCU ESP8266 bench prototype where physically connected.
- Gateway: Windows laptop running the Python serial gateway and FastAPI stack.
- Current live-capable transport: USB Serial. Simulation uses the same authenticated ingestion service but remains labelled `SIMULATION`.
- Raspberry Pi, LoRa, LoRaWAN, NB-IoT, cellular, 5G, solar power, and field enclosures are not claimed as deployed.

## Planned field architecture

- JALA may retain the ESP8266 prototype or move to ESP32.
- AGNI, BHUMI, VAYU, and AKASHA use ESP32-class controllers.
- One shared Raspberry Pi-class Linux gateway may provide local services, cache, processing, synchronization, store-forward, and a dashboard.
- Raspberry Pi is a gateway class, not a mandatory controller for every sensor node, and remains `PLANNED` until physically connected.

Hardware profiles record controller, sensors, transport capability state, power, enclosure, firmware, provenance, and capabilities. Transport states are `LIVE`, `SUPPORTED`, `PLANNED`, or `UNAVAILABLE`.

Cost efficiency comes from modular hazard-specific sensors, shared environmental observations, strategic placement, open-source software, authoritative external data, adaptive sampling, phased deployment, and avoiding duplicate hardware. Expensive sensors remain optional until a site-specific requirement justifies them.
