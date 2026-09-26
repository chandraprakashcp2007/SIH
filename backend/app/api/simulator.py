"""
Disaster Simulator API Router
Controls scenarios, manual slider overrides, and simulation lifecycle.
"""
from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.services.simulation_service import simulation_service
from gateway.simulator import prahari_sim
from backend.app.models.audit import AuditLog

router = APIRouter(prefix="/simulator", tags=["Simulator"])

SCENARIOS = [
    {"id": "ALL_NORMAL", "name": "All Normal Baseline", "hazard": "GENERAL", "desc": "All nodes operate within healthy, nominal environmental baselines."},
    {"id": "FLOOD_RAMP", "name": "Flood Water Ramp", "hazard": "FLOOD", "desc": "Gradual river rise transitioning JALA from Normal -> Watch -> Warning -> Critical."},
    {"id": "FLASH_FLOOD", "name": "Torrential Flash Flood", "hazard": "FLOOD", "desc": "Rapid extreme water rise surge with high velocity and acceleration."},
    {"id": "FIRE_DEVELOPMENT", "name": "Wildfire Development", "hazard": "FIRE", "desc": "Progressive combustion: smoke rises, followed by temperature, flame, and AI camera confirmation."},
    {"id": "FALSE_SMOKE_SENSOR_SPIKE", "name": "False Smoke Sensor Spike", "hazard": "FIRE", "desc": "MQ-2 spikes in isolation; thermal & optical sensors normal; Trust engine suppresses false alarm."},
    {"id": "CONFIRMED_FIRE", "name": "Immediate Confirmed Fire", "hazard": "FIRE", "desc": "Full thermal surge, smoke plume, and active optical flame detection."},
    {"id": "LANDSLIDE_SATURATION", "name": "Rain Soil Saturation", "hazard": "LANDSLIDE", "desc": "Prolonged rainfall context drives pore water pressure to saturation levels."},
    {"id": "LANDSLIDE_MOVEMENT", "name": "Active Landslide Shear Slip", "hazard": "LANDSLIDE", "desc": "Saturated slope experiences structural tilt delta and high vibration RMS."},
    {
        "id": "AIR_QUALITY_EVENT",
        "name": "VAYU Air Quality Escalation",
        "hazard": "AIR_QUALITY",
        "desc": "PM, CO and VOC indicators rise together."
    },
    {
        "id": "SEVERE_WEATHER",
        "name": "AKASHA Severe Weather Escalation",
        "hazard": "EXTREME_WEATHER",
        "desc": "Rain, wind, gust and pressure-fall evidence rise together."
    },
    {"id": "SENSOR_FAILURE", "name": "Sensor Freeze / Out-of-Bounds", "hazard": "GENERAL", "desc": "Sensor value jumps out-of-bounds; trust decays to 30% without panic alert."},
    {"id": "NODE_OFFLINE", "name": "Node Power Cut / Disconnect", "hazard": "GENERAL", "desc": "JALA-01 stops emitting packets; gateway flags node as OFFLINE."},
    {"id": "PACKET_LOSS", "name": "LoRa RF Interference & Gaps", "hazard": "GENERAL", "desc": "Simulates 35% packet drops causing sequence gaps and packet loss warnings."},
    {"id": "INTERNET_OUTAGE", "name": "Internet Severed (Local Edge)", "hazard": "GENERAL", "desc": "Simulates WAN failure; system continues in autonomous LOCAL EDGE mode."},
    {"id": "RECOVERY", "name": "Environmental Recovery", "hazard": "GENERAL", "desc": "Conditions return to safe thresholds; alerts automatically resolve."},
    {"id": "RESET", "name": "Factory Reset Demo", "hazard": "GENERAL", "desc": "Clears test anomalies and returns telemetry to clean initial state."}
]


class ManualOverrideRequest(BaseModel):
    node_id: str
    metrics: Dict[str, Any]


@router.get("/scenarios")
async def get_scenarios():
    """Retrieve all available physical disaster simulation scenarios."""
    return {
        "active_scenario": simulation_service.active_scenario,
        "is_running": simulation_service.is_running,
        "internet_outage": prahari_sim.internet_outage,
        "scenarios": SCENARIOS
    }


@router.post("/start")
async def start_simulator(db: AsyncSession = Depends(get_db)):
    """Start continuous simulation loop."""
    await simulation_service.start()
    db.add(AuditLog(
        action="SIMULATOR_STARTED",
        category="SIMULATOR",
        component="simulator",
        message="Simulation engine resumed continuous telemetry generation."
    ))
    await db.commit()
    return {"status": "started", "active_scenario": simulation_service.active_scenario}


@router.post("/stop")
async def stop_simulator(db: AsyncSession = Depends(get_db)):
    """Pause continuous simulation loop."""
    await simulation_service.stop()
    db.add(AuditLog(
        action="SIMULATOR_STOPPED",
        category="SIMULATOR",
        component="simulator",
        message="Simulation engine paused."
    ))
    await db.commit()
    return {"status": "stopped"}


@router.post("/reset")
async def reset_simulator(db: AsyncSession = Depends(get_db)):
    """Reset all nodes to nominal baseline values."""
    simulation_service.set_scenario("RESET")
    db.add(AuditLog(
        action="SIMULATOR_RESET",
        category="SIMULATOR",
        component="simulator",
        message="Simulation state reset to nominal environmental baselines."
    ))
    await db.commit()
    return {"status": "reset", "active_scenario": "ALL_NORMAL"}


@router.post("/scenario/{scenario_name}")
async def trigger_scenario(scenario_name: str, db: AsyncSession = Depends(get_db)):
    """Engage a specific disaster simulation scenario."""
    valid_names = [s["id"] for s in SCENARIOS]
    if scenario_name not in valid_names:
        raise HTTPException(status_code=400, detail=f"Invalid scenario '{scenario_name}'. Valid: {valid_names}")

    res = simulation_service.set_scenario(scenario_name)
    db.add(AuditLog(
        action="SCENARIO_ENGAGED",
        category="SIMULATOR",
        component="simulator",
        message=f"Simulation scenario '{scenario_name}' engaged.",
        details={"scenario": scenario_name}
    ))
    await db.commit()
    return res


@router.post("/manual")
async def manual_override(req: ManualOverrideRequest):
    """Set manual telemetry values from interactive dashboard sliders."""
    if req.node_id in prahari_sim.state:
        for k, v in req.metrics.items():
            prahari_sim.state[req.node_id][k] = v
        return {"status": "updated", "node_id": req.node_id, "state": prahari_sim.state[req.node_id]}
    raise HTTPException(status_code=404, detail="Node ID not found in simulation state")
