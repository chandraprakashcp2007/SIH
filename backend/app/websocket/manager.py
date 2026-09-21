"""
PRAHARI-NET Real-Time WebSocket Connection Manager
Broadcasts typed JSON events to connected browser and PWA command-centre clients.
"""
import json
import logging
from typing import Set, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger("prahari.websocket")


class ConnectionManager:
    """Manages active WebSocket sessions and broadcasts typed disaster telemetry."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, subprotocol: str | None = None):
        await websocket.accept(subprotocol=subprotocol)
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining clients: {len(self.active_connections)}")

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast typed event message to all connected clients."""
        if not self.active_connections:
            return

        payload = {
            "type": event_type,
            "data": data
        }
        message_text = json.dumps(payload, default=str)
        dead_connections = []

        for connection in list(self.active_connections):
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.warning(f"Error sending to WebSocket client: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)


ws_manager = ConnectionManager()
