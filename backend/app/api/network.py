"""
Network & RF Topology Status API Router
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.network import GatewayPacketLog
from backend.app.models.nodes import Node
from backend.app.websocket.manager import ws_manager
from backend.app.core.config import settings
from gateway.simulator import prahari_sim
from backend.app.services.readiness_service import get_gateway_state

router = APIRouter(prefix="/network", tags=["Network"])


@router.get("/status")
async def network_status(db: AsyncSession = Depends(get_db)):
    """Network topology state, LoRa RF link health, and gateway metrics."""
    nodes_res = await db.execute(select(Node))
    nodes = nodes_res.scalars().all()

    pkts_res = await db.execute(
        select(GatewayPacketLog)
        .order_by(desc(GatewayPacketLog.timestamp))
        .limit(100)
    )
    recent_pkts = pkts_res.scalars().all()

    total = len(recent_pkts)
    duplicates = len([p for p in recent_pkts if p.is_duplicate])
    rejected = len([p for p in recent_pkts if not p.is_valid])
    gaps = sum(p.sequence_gap for p in recent_pkts)

    network_mode = "LOCAL_EDGE" if prahari_sim.internet_outage else "ONLINE"

    node_stats = []
    for n in nodes:
        node_stats.append({
            "node_id": n.id,
            "name": n.name,
            "rssi": n.signal_rssi,
            "packet_loss_pct": n.packet_loss_pct,
            "status": n.status,
            "last_seen": n.last_seen.isoformat()
        })

    gateway = await get_gateway_state(db)
    return {
        "gateway_status": gateway["status"],
        "gateway": gateway,
        "gateway_mode": settings.GATEWAY_MODE,
        "serial_port": settings.SERIAL_PORT,
        "baud_rate": settings.SERIAL_BAUD_RATE,
        "network_mode": network_mode,
        "websocket_clients": len(ws_manager.active_connections),
        "total_packets_recent": total,
        "duplicate_packets": duplicates,
        "rejected_packets": rejected,
        "sequence_gaps": gaps,
        "nodes": node_stats
    }


@router.get("/packets")
async def network_packets(limit: int = 30, db: AsyncSession = Depends(get_db)):
    """Retrieve raw stream of recently logged gateway packets."""
    pkts_res = await db.execute(
        select(GatewayPacketLog)
        .order_by(desc(GatewayPacketLog.timestamp))
        .limit(limit)
    )
    records = pkts_res.scalars().all()
    return [
        {
            "id": p.id,
            "node_id": p.node_id,
            "sequence": p.sequence,
            "timestamp": p.timestamp.isoformat(),
            "rssi": p.rssi,
            "is_valid": p.is_valid,
            "is_duplicate": p.is_duplicate,
            "sequence_gap": p.sequence_gap,
            "gateway_source": p.gateway_source,
            "rejection_reason": p.rejection_reason
        }
        for p in records
    ]
