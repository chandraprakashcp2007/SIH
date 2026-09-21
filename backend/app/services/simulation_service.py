"""
PRAHARI-NET Backend Simulation Service
Manages background simulation loop, scenario changes, and direct pipeline ingestion.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import AsyncSessionLocal
from backend.app.services.telemetry_service import telemetry_service
from gateway.simulator import prahari_sim
from backend.app.websocket.manager import ws_manager

logger = logging.getLogger("prahari.sim_service")


class SimulationService:
    """Orchestrates in-process simulation loop and scenario switching."""

    def __init__(self):
        self.is_running = True
        self.task: Optional[asyncio.Task] = None
        self.tick_rate_sec = 2.0
        self.active_scenario = "ALL_NORMAL"

    async def start(self):
        if self.task is None or self.task.done():
            self.is_running = True
            self.task = asyncio.create_task(self._simulation_loop())
            logger.info("Simulation service background task started.")

    async def stop(self):
        self.is_running = False
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Simulation service background task stopped.")

    def set_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Trigger one of the 14 standard disaster scenarios."""
        prahari_sim.set_scenario(scenario_name)
        self.active_scenario = scenario_name
        logger.info(f"Simulation scenario switched to: {scenario_name}")
        return {
            "status": "success",
            "active_scenario": scenario_name,
            "message": f"Scenario '{scenario_name}' engaged."
        }

    async def _simulation_loop(self):
        """Ticks simulation state and forwards directly into telemetry_service."""
        while self.is_running:
            try:
                await asyncio.sleep(self.tick_rate_sec)
                prahari_sim.step_simulation()
                packets = prahari_sim.generate_packets()

                # Process through the real telemetry service in a database session
                async with AsyncSessionLocal() as db:
                    for node_id, pkt in packets.items():
                        await telemetry_service.ingest_packet(
                            db=db,
                            payload=pkt,
                            gateway_source="SIMULATOR"
                        )

                # Broadcast simulation status to WebSocket clients
                await ws_manager.broadcast_event("simulation.updated", {
                    "is_running": self.is_running,
                    "active_scenario": self.active_scenario,
                    "tick": prahari_sim.tick,
                    "internet_outage": prahari_sim.internet_outage
                })

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in simulation loop: {e}", exc_info=True)
                await asyncio.sleep(2.0)


simulation_service = SimulationService()
