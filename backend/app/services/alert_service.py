"""
PRAHARI-NET Alert & Incident Management Service
Handles alert lifecycle, deduplication, escalation, acknowledgement, and resolution.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.alerts import Alert
from backend.app.models.audit import AuditLog
from backend.app.websocket.manager import ws_manager


class AlertService:
    """Manages disaster incident lifecycle according to NDMA CAP standards."""

    HAZARD_MAP = {
        "JALA-01": ("FLOOD", "SIMULATION DEMO LOCATION"),
        "AGNI-02": ("FIRE", "SIMULATION DEMO LOCATION"),
        "BHUMI-03": ("LANDSLIDE", "SIMULATION DEMO LOCATION")
    }

    async def evaluate_and_create_alert(
        self,
        db: AsyncSession,
        node_id: str,
        risk_score: float,
        risk_band: str,
        confidence: float,
        explanation: str,
        action_recommended: str,
        evidence: Dict[str, Any]
    ) -> Optional[Alert]:
        """
        Creates or escalates alerts based on risk transitions.
        Deduplicates repeated samples so operators aren't flooded with duplicates.
        """
        hazard_type, default_loc = self.HAZARD_MAP.get(node_id, ("HAZARD", "Monitoring Zone 1"))

        # If risk returned to NORMAL, resolve any active alerts for this node
        if risk_band == "NORMAL":
            await self._auto_resolve_if_active(db, node_id)
            return None

        # Check for existing un-resolved alert for this node
        query = (
            select(Alert)
            .where(Alert.node_id == node_id, Alert.state.in_(["NEW", "ACKNOWLEDGED", "MONITORING"]))
            .order_by(desc(Alert.created_at))
            .limit(1)
        )
        result = await db.execute(query)
        existing_alert = result.scalar_one_or_none()

        headline = f"{risk_band} {hazard_type} DETECTED AT {node_id}"

        if existing_alert:
            # If severity changed (e.g. WATCH -> WARNING -> CRITICAL), escalate it
            if existing_alert.severity != risk_band:
                existing_alert.severity = risk_band
                existing_alert.risk_score = risk_score
                existing_alert.confidence = confidence
                existing_alert.headline = headline
                existing_alert.summary = explanation
                existing_alert.action_recommended = action_recommended
                existing_alert.evidence = evidence
                await db.commit()
                await db.refresh(existing_alert)

                # Broadcast update
                await ws_manager.broadcast_event("alert.updated", {
                    "alert_id": existing_alert.id,
                    "node_id": node_id,
                    "severity": risk_band,
                    "risk_score": risk_score,
                    "headline": headline
                })
            return existing_alert

        # Otherwise create new alert
        new_alert = Alert(
            id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            severity=risk_band,
            hazard=hazard_type,
            node_id=node_id,
            location_name=default_loc,
            created_at=datetime.now(timezone.utc),
            state="NEW",
            confidence=confidence,
            risk_score=risk_score,
            headline=headline,
            summary=explanation,
            action_recommended=action_recommended,
            evidence=evidence
        )
        db.add(new_alert)

        # Audit log entry
        audit = AuditLog(
            action="ALERT_TRIGGERED",
            category="ALERT",
            component="alert_service",
            message=f"Incident {new_alert.id} generated: {headline} (Risk: {risk_score}%)",
            details={"alert_id": new_alert.id, "node_id": node_id, "severity": risk_band, "risk_score": risk_score}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(new_alert)

        # Real-time notification broadcast
        await ws_manager.broadcast_event("alert.created", {
            "id": new_alert.id,
            "severity": new_alert.severity,
            "hazard": new_alert.hazard,
            "node_id": new_alert.node_id,
            "location_name": new_alert.location_name,
            "created_at": new_alert.created_at.isoformat(),
            "confidence": new_alert.confidence,
            "risk_score": new_alert.risk_score,
            "headline": new_alert.headline,
            "summary": new_alert.summary,
            "action_recommended": new_alert.action_recommended
        })

        return new_alert

    async def acknowledge_alert(
        self,
        db: AsyncSession,
        alert_id: str,
        acknowledged_by: str,
        notes: Optional[str] = None
    ) -> Optional[Alert]:
        """Acknowledge incident by operator."""
        query = select(Alert).where(Alert.id == alert_id)
        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        alert.state = "ACKNOWLEDGED"
        alert.acknowledged_at = datetime.now(timezone.utc)
        alert.acknowledged_by = acknowledged_by
        if notes:
            alert.resolution_notes = (alert.resolution_notes or "") + f"\n[Ack Notes: {notes}]"

        audit = AuditLog(
            action="ALERT_ACKNOWLEDGED",
            category="ALERT",
            component="alert_service",
            user_id=acknowledged_by,
            username=acknowledged_by,
            message=f"Alert {alert_id} acknowledged by {acknowledged_by}",
            details={"alert_id": alert_id, "notes": notes}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(alert)

        await ws_manager.broadcast_event("alert.acknowledged", {
            "alert_id": alert_id,
            "acknowledged_by": acknowledged_by,
            "state": "ACKNOWLEDGED"
        })

        return alert

    async def resolve_alert(
        self,
        db: AsyncSession,
        alert_id: str,
        resolved_by: str,
        resolution_notes: str
    ) -> Optional[Alert]:
        """Resolve incident with required operational notes."""
        query = select(Alert).where(Alert.id == alert_id)
        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        alert.state = "RESOLVED"
        alert.resolved_at = datetime.now(timezone.utc)
        alert.resolved_by = resolved_by
        alert.resolution_notes = resolution_notes

        audit = AuditLog(
            action="ALERT_RESOLVED",
            category="ALERT",
            component="alert_service",
            user_id=resolved_by,
            username=resolved_by,
            message=f"Alert {alert_id} resolved by {resolved_by}: {resolution_notes}",
            details={"alert_id": alert_id, "resolution_notes": resolution_notes}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(alert)

        await ws_manager.broadcast_event("alert.resolved", {
            "alert_id": alert_id,
            "resolved_by": resolved_by,
            "state": "RESOLVED"
        })

        return alert

    async def _auto_resolve_if_active(self, db: AsyncSession, node_id: str):
        query = (
            select(Alert)
            .where(Alert.node_id == node_id, Alert.state.in_(["NEW", "ACKNOWLEDGED", "MONITORING"]))
        )
        result = await db.execute(query)
        active_alerts = result.scalars().all()
        for a in active_alerts:
            a.state = "RESOLVED"
            a.resolved_at = datetime.now(timezone.utc)
            a.resolved_by = "SYSTEM_AUTO_RECOVERY"
            a.resolution_notes = "Hazard indicators returned to nominal baseline."
            await ws_manager.broadcast_event("alert.resolved", {
                "alert_id": a.id,
                "resolved_by": "SYSTEM_AUTO_RECOVERY",
                "state": "RESOLVED"
            })
        if active_alerts:
            await db.commit()


alert_service = AlertService()
