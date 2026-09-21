"""
PRAHARI Copilot Permissions & Safety Enforcement
Strictly enforces read-only operations and RBAC.
"""
from typing import List, Dict, Any, Set
from fastapi import HTTPException, status

READ_ONLY_DISALLOWED_ACTIONS: Set[str] = {
    "acknowledge_alert",
    "resolve_alert",
    "modify_risk_score",
    "override_threshold",
    "start_simulation",
    "stop_simulation",
    "set_scenario",
    "modify_setting",
    "delete_data",
    "reboot_gateway",
}

ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "ADMIN": {"read", "metrics", "sessions_all", "docs_rebuild"},
    "OPERATOR": {"read", "sessions_own"},
    "VIEWER": {"read", "sessions_own"}
}


class PermissionGuard:
    """Enforces absolute read-only policy for Copilot."""

    @staticmethod
    def verify_read_only(action_name: str):
        if action_name.lower() in READ_ONLY_DISALLOWED_ACTIONS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Security Policy Violation: Action '{action_name}' is disallowed. Copilot is strictly read-only."
            )

    @staticmethod
    def can_access_metrics(role: str) -> bool:
        return role == "ADMIN"

    @staticmethod
    def can_rebuild_index(role: str) -> bool:
        return role == "ADMIN"


permission_guard = PermissionGuard()
