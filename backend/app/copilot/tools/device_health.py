"""
Copilot Device Health & Maintenance Tools
Monitors solar charging, battery levels, RF signal, and calibration flags.
"""
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.nodes import Node


async def get_device_health(db: AsyncSession) -> Dict[str, Any]:
    """Retrieve battery voltage, solar power, and hardware diagnostics across fleet."""
    res = await db.execute(select(Node))
    nodes = res.scalars().all()

    fleet_health = []
    low_battery_nodes = []

    for n in nodes:
        fleet_health.append({
            "node_id": n.id,
            "name": n.name,
            "status": n.status,
            "battery_pct": n.battery_pct,
            "solar_voltage": n.solar_voltage,
            "firmware": n.firmware_version,
            "hardware_rev": n.hardware_rev
        })
        if n.battery_pct < 25.0:
            low_battery_nodes.append(n.id)

    return {
        "nodes": fleet_health,
        "nodes_online": len([n for n in nodes if n.status != "OFFLINE"]),
        "low_battery_nodes": low_battery_nodes,
        "all_healthy": len(low_battery_nodes) == 0
    }


async def get_maintenance_flags(db: AsyncSession) -> List[Dict[str, Any]]:
    """Flags any sensor node requiring field battery replacement, firmware upgrade, or realignment."""
    res = await db.execute(select(Node))
    nodes = res.scalars().all()
    flags = []

    for n in nodes:
        if n.battery_pct < 25.0:
            flags.append({
                "node_id": n.id,
                "type": "LOW_BATTERY",
                "message": f"Battery critically low at {n.battery_pct}%. Immediate solar/battery check needed."
            })
        if n.signal_rssi < -95:
            flags.append({
                "node_id": n.id,
                "type": "WEAK_RF_LINK",
                "message": f"RSSI is {n.signal_rssi} dBm. Inspect line-of-sight antenna orientation."
            })
        if n.packet_loss_pct > 10.0:
            flags.append({
                "node_id": n.id,
                "type": "HIGH_PACKET_LOSS",
                "message": f"Packet loss rate is {n.packet_loss_pct}%. Potential RF interference."
            })

    return flags
