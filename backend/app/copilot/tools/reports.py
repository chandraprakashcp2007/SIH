"""
Copilot User Permissions & Shift Briefing Tools
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.copilot.tools.system import get_system_summary
from backend.app.copilot.tools.alerts import get_active_alerts


async def get_current_user_permissions(role: str = "OPERATOR") -> Dict[str, Any]:
    """Retrieve operational role and allowed commands for the currently authenticated user."""
    return {
        "role": role,
        "read_only": True,
        "allowed_capabilities": ["inquire_status", "view_causal_evidence", "inspect_rf", "read_docs"],
        "restricted_actions": ["acknowledge_alert", "resolve_alert", "recalibrate_thresholds"]
    }


async def get_operator_briefing(db: AsyncSession) -> Dict[str, Any]:
    """Compile an executive shift briefing summarizing system status, alerts, and node risks."""
    summary = await get_system_summary(db)
    alerts = await get_active_alerts(db)
    return {
        "system_summary": summary,
        "active_incidents": alerts,
        "briefing_status": "CRITICAL" if summary.get("critical_alerts_count", 0) > 0 else "NOMINAL"
    }
