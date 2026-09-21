"""
Copilot Network & Gateway Tools
Assesses LoRa RF link health, RSSI, sequence gaps, and concentrator connectivity.
"""
from typing import Dict, Any, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.network import GatewayPacketLog
from backend.app.models.nodes import Node
from backend.app.core.config import settings
from gateway.simulator import prahari_sim
from backend.app.services.readiness_service import get_gateway_state


async def get_network_status(db: AsyncSession) -> Dict[str, Any]:
    """Retrieve overall RF topology health, weakest node RSSI, and packet loss."""
    nodes_res = await db.execute(select(Node))
    nodes = nodes_res.scalars().all()

    pkts_res = await db.execute(
        select(GatewayPacketLog)
        .order_by(desc(GatewayPacketLog.timestamp))
        .limit(60)
    )
    pkts = pkts_res.scalars().all()

    weakest = min(nodes, key=lambda n: n.signal_rssi) if nodes else None

    return {
        "gateway_mode": settings.GATEWAY_MODE,
        "serial_port": settings.SERIAL_PORT,
        "total_nodes": len(nodes),
        "weakest_node_id": weakest.id if weakest else None,
        "weakest_rssi_dbm": weakest.signal_rssi if weakest else None,
        "average_rssi_dbm": round(sum(n.signal_rssi for n in nodes) / max(1, len(nodes)), 1) if nodes else -75.0,
        "average_packet_loss_pct": round(sum(n.packet_loss_pct for n in nodes) / max(1, len(nodes)), 1) if nodes else 0.0,
        "network_mode": "LOCAL_EDGE" if prahari_sim.internet_outage else "ONLINE",
        "recent_packet_count": len(pkts)
    }


async def get_gateway_status(db: AsyncSession) -> Dict[str, Any]:
    """Verify PRAHARI gateway concentrator interface and physical connection."""
    state = await get_gateway_state(db)
    return {
        **state,
        "mode": settings.GATEWAY_MODE,
        "port": settings.SERIAL_PORT,
        "baud_rate": settings.SERIAL_BAUD_RATE,
        "protocol": "PRAHARI-LORA-JSON-v1",
        "internet_connected": not prahari_sim.internet_outage,
        "autonomous_edge": True
    }


async def get_packet_statistics(db: AsyncSession) -> Dict[str, Any]:
    """Calculate duplicate counts, sequence gaps, and validity of logged packets."""
    pkts_res = await db.execute(
        select(GatewayPacketLog)
        .order_by(desc(GatewayPacketLog.timestamp))
        .limit(100)
    )
    recent = pkts_res.scalars().all()
    total = len(recent)
    valid = len([p for p in recent if p.is_valid])
    duplicates = len([p for p in recent if p.is_duplicate])
    gaps = sum(p.sequence_gap for p in recent)

    return {
        "sampled_packets": total,
        "valid_packets": valid,
        "duplicate_packets": duplicates,
        "sequence_gaps_detected": gaps,
        "packet_delivery_rate_pct": round((valid / max(1, total)) * 100.0, 1) if total else 100.0
    }
