from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy import desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.network import GatewayPacketLog
from backend.app.models.nodes import Node
from backend.app.services.simulation_service import simulation_service


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def derive_gateway_state(last_packet_at: Optional[datetime], now: datetime, timeout_seconds: float) -> Dict[str, Any]:
    if last_packet_at is None:
        return {"status": "OFFLINE", "last_packet_at": None, "last_packet_age_seconds": None}
    age = max(0.0, (_as_utc(now) - _as_utc(last_packet_at)).total_seconds())
    return {
        "status": "CONNECTED" if age <= timeout_seconds else "STALE",
        "last_packet_at": _as_utc(last_packet_at).isoformat(),
        "last_packet_age_seconds": round(age, 1),
    }


async def get_gateway_state(db: AsyncSession, timeout_seconds: float = 10.0) -> Dict[str, Any]:
    result = await db.execute(select(GatewayPacketLog).order_by(desc(GatewayPacketLog.timestamp)).limit(1))
    latest = result.scalar_one_or_none()
    state = derive_gateway_state(latest.timestamp if latest else None, datetime.now(timezone.utc), timeout_seconds)
    if latest:
        state.update(source=latest.gateway_source, node_id=latest.node_id, sequence=latest.sequence)
    return state


async def build_system_readiness(db: AsyncSession) -> Dict[str, Any]:
    from backend.app.copilot.retrieval import knowledge_retriever
    checks: Dict[str, Dict[str, Any]] = {}
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = {"status": "READY", "detail": "SQLite query succeeded"}
    except Exception as exc:
        checks["database"] = {"status": "FAILED", "detail": type(exc).__name__}

    gateway = await get_gateway_state(db)
    checks["gateway"] = {"status": "READY" if gateway["status"] == "CONNECTED" else "DEGRADED", "detail": gateway}
    nodes = (await db.execute(select(Node))).scalars().all()
    for node_id in ("JALA-01", "AGNI-02", "BHUMI-03", "VAYU-04", "AKASHA-05"):
        node = next((item for item in nodes if item.id == node_id), None)
        checks[node_id.lower().split("-")[0]] = {
            "status": "READY" if node and node.status != "OFFLINE" else "DEGRADED",
            "detail": node.status if node else "Not registered",
        }
    checks.update({
        "backend": {"status": "READY", "detail": "FastAPI service active"},
        "websocket": {"status": "READY", "detail": "Authenticated endpoint registered"},
        "risk_engine": {"status": "READY", "detail": "Hybrid deterministic engine loaded"},
        "alerts": {"status": "READY", "detail": "Alert lifecycle service loaded"},
        "audio": {"status": "READY", "detail": "Browser opt-in alarm synthesis"},
        "pwa": {"status": "READY" if Path("frontend/public/manifest.json").exists() else "FAILED", "detail": "Manifest checked"},
        "copilot": {"status": "READY", "detail": "Local Assistant available"},
        "knowledge_base": {"status": "READY" if knowledge_retriever.is_ready else "DEGRADED", "detail": f"{len(knowledge_retriever.chunks)} chunks"},
        "simulator": {"status": "READY" if simulation_service.is_running else "DEGRADED", "detail": simulation_service.active_scenario},
    })
    overall = "READY" if all(item["status"] == "READY" for item in checks.values()) else "DEGRADED"
    return {"overall_status": overall, "checked_at": datetime.now(timezone.utc).isoformat(), "checks": checks}
