"""
Copilot System Tools
Implements system status, operational mode, system readiness, and demo status tools.
"""
from typing import Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.nodes import Node
from backend.app.models.alerts import Alert
from backend.app.models.risk import RiskAssessment
from backend.app.core.config import settings
from gateway.simulator import prahari_sim
from backend.app.services.readiness_service import build_system_readiness, get_gateway_state
from backend.app.services.simulation_service import simulation_service


async def get_system_summary(db: AsyncSession) -> Dict[str, Any]:
    """Retrieve comprehensive platform overview metrics."""
    nodes_res = await db.execute(select(Node))
    nodes = nodes_res.scalars().all()

    alerts_res = await db.execute(
        select(Alert).where(Alert.state.in_(["NEW", "ACKNOWLEDGED", "MONITORING"]))
    )
    active_alerts = alerts_res.scalars().all()

    risks_res = await db.execute(
        select(RiskAssessment).order_by(desc(RiskAssessment.timestamp)).limit(3)
    )
    risks = risks_res.scalars().all()
    avg_risk = round(sum(r.risk_score for r in risks) / max(1, len(risks)), 1) if risks else 0.0

    gateway = await get_gateway_state(db)
    return {
        "nodes_total": len(nodes),
        "nodes_online": len([n for n in nodes if n.status != "OFFLINE"]),
        "active_alerts_count": len(active_alerts),
        "critical_alerts_count": len([a for a in active_alerts if a.severity == "CRITICAL"]),
        "warning_alerts_count": len([a for a in active_alerts if a.severity == "WARNING"]),
        "average_risk_score": avg_risk,
        "gateway_status": gateway["status"],
        "last_packet_age_seconds": gateway["last_packet_age_seconds"],
        "gateway_mode": settings.GATEWAY_MODE,
        "is_simulation": prahari_sim.active_scenario != "REAL_HARDWARE"
    }


async def get_current_operational_mode(db: AsyncSession) -> Dict[str, Any]:
    """Check whether system is running online or in autonomous offline local edge mode."""
    is_offline = prahari_sim.internet_outage
    return {
        "network_mode": "LOCAL_EDGE" if is_offline else "ONLINE",
        "autonomous_sovereign": is_offline,
        "internet_connected": not is_offline,
        "gateway_mode": settings.GATEWAY_MODE,
        "active_scenario": prahari_sim.active_scenario,
        "copilot_mode": settings.COPILOT_MODE
    }


async def get_system_readiness(db: AsyncSession) -> Dict[str, Any]:
    """Diagnostic check for backend, database, risk engine, LoRa gateway, and copilot readiness."""
    return await build_system_readiness(db)


async def get_demo_mode_status(db: AsyncSession) -> Dict[str, Any]:
    """Status of active disaster simulation board scenario."""
    return {
        "is_simulation": simulation_service.is_running,
        "active_scenario": prahari_sim.active_scenario,
        "simulation_tick": prahari_sim.tick,
        "internet_outage_simulated": prahari_sim.internet_outage,
        "packet_loss_mode": prahari_sim.packet_loss_mode
    }
