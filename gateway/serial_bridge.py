"""
PRAHARI-NET Gateway & Hardware Serial Bridge
Reads JSON lines from USB Serial (Arduino / ESP32 LoRa Receiver) or runs Simulator mode.
Forwards validated packets to local FastAPI backend /api/telemetry/ingest.
"""
import os
import sys
import time
import json
import logging
import asyncio
import httpx
from typing import Optional

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("prahari.gateway")

SERIAL_PORT = os.getenv("SERIAL_PORT", "COM3")
SERIAL_BAUD_RATE = int(os.getenv("SERIAL_BAUD_RATE", "115200"))
BACKEND_INGEST_URL = os.getenv("BACKEND_INGEST_URL", "http://127.0.0.1:8000/api/telemetry/ingest")
BACKEND_AUTH_URL = os.getenv("BACKEND_AUTH_URL", "http://127.0.0.1:8000/api/auth/login")
GATEWAY_USERNAME = os.getenv("GATEWAY_USERNAME", "gateway")
GATEWAY_PASSWORD = os.getenv("GATEWAY_PASSWORD", "prahari-gateway-local")
GATEWAY_MODE = os.getenv("GATEWAY_MODE", "SIMULATOR").upper()  # REAL or SIMULATOR


class SerialBridge:
    """LoRa gateway serial listener and forwarder."""

    def __init__(self, port: str = SERIAL_PORT, baudrate: int = SERIAL_BAUD_RATE, mode: str = GATEWAY_MODE):
        self.port = port
        self.baudrate = baudrate
        self.mode = mode
        self.running = False
        self.packets_received = 0
        self.packets_forwarded = 0
        self.packets_rejected = 0
        self.access_token: Optional[str] = None

    async def authenticate(self, client: httpx.AsyncClient) -> bool:
        try:
            response = await client.post(BACKEND_AUTH_URL, json={"username": GATEWAY_USERNAME, "password": GATEWAY_PASSWORD}, timeout=3.0)
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
            return True
        except Exception as exc:
            logger.error(f"Gateway authentication failed: {exc}")
            self.access_token = None
            return False

    def validate_packet(self, data: dict) -> bool:
        """Enforces schema compliance for LoRa packets."""
        required = ["version", "node_id", "sequence", "metrics", "rssi"]
        if not all(k in data for k in required):
            return False
        if data["node_id"] not in ["JALA-01", "AGNI-02", "BHUMI-03"]:
            return False
        if not isinstance(data["metrics"], dict):
            return False
        return True

    async def forward_to_backend(self, client: httpx.AsyncClient, packet: dict):
        """HTTP POST to local ingestion endpoint."""
        try:
            if not self.access_token and not await self.authenticate(client):
                self.packets_rejected += 1
                return
            headers = {"Authorization": f"Bearer {self.access_token}"}
            resp = await client.post(BACKEND_INGEST_URL, json=packet, headers=headers, timeout=3.0)
            if resp.status_code == 401 and await self.authenticate(client):
                headers = {"Authorization": f"Bearer {self.access_token}"}
                resp = await client.post(BACKEND_INGEST_URL, json=packet, headers=headers, timeout=3.0)
            if resp.status_code == 200:
                self.packets_forwarded += 1
                logger.info(f"Forwarded {packet['node_id']} seq {packet['sequence']} -> Status {resp.status_code}")
            else:
                logger.warning(f"Backend rejected packet: {resp.status_code} {resp.text}")
                self.packets_rejected += 1
        except Exception as e:
            logger.error(f"Failed to post to backend at {BACKEND_INGEST_URL}: {e}")
            self.packets_rejected += 1

    async def run_simulator(self):
        """Autonomous simulation loop."""
        from gateway.simulator import prahari_sim
        logger.info("Starting Gateway in SIMULATOR mode...")
        async with httpx.AsyncClient() as client:
            while self.running:
                prahari_sim.step_simulation()
                packets = prahari_sim.generate_packets()
                for node_id, pkt in packets.items():
                    self.packets_received += 1
                    if self.validate_packet(pkt):
                        await self.forward_to_backend(client, pkt)
                    else:
                        self.packets_rejected += 1
                await asyncio.sleep(2.0)

    async def run_real_serial(self):
        """Connects to real USB COM port and reads newline-delimited JSON."""
        try:
            import serial
        except ImportError:
            logger.error("pyserial is required for REAL serial mode. Run: pip install pyserial")
            return

        logger.info(f"Connecting to hardware Serial on {self.port} at {self.baudrate} baud...")
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=1.0)
            logger.info(f"Connected to hardware LoRa receiver on {self.port}.")
        except Exception as e:
            logger.error(f"Failed to open serial port {self.port}: {e}")
            logger.info("Falling back to SIMULATOR mode...")
            await self.run_simulator()
            return

        async with httpx.AsyncClient() as client:
            loop = asyncio.get_event_loop()
            while self.running:
                try:
                    line = await loop.run_in_executor(None, ser.readline)
                    if not line:
                        continue
                    line_str = line.decode('utf-8', errors='ignore').strip()
                    if not line_str.startswith('{'):
                        continue
                    
                    self.packets_received += 1
                    packet = json.loads(line_str)
                    if self.validate_packet(packet):
                        await self.forward_to_backend(client, packet)
                    else:
                        self.packets_rejected += 1
                        logger.warning(f"Malformed packet rejected: {line_str}")
                except json.JSONDecodeError:
                    self.packets_rejected += 1
                    logger.warning(f"Invalid JSON string received on {self.port}")
                except Exception as ex:
                    logger.error(f"Serial read error: {ex}")
                    await asyncio.sleep(1.0)

    async def start(self):
        self.running = True
        if self.mode == "REAL":
            await self.run_real_serial()
        else:
            await self.run_simulator()

    def stop(self):
        self.running = False


if __name__ == "__main__":
    bridge = SerialBridge()
    try:
        asyncio.run(bridge.start())
    except KeyboardInterrupt:
        bridge.stop()
        logger.info("Gateway bridge stopped.")
