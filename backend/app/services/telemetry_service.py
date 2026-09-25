"""
PRAHARI-NET Telemetry Ingestion & Real-Time Processing Service
Processes packets from serial LoRa and simulator pipelines.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.telemetry import TelemetryRecord
from backend.app.models.risk import RiskAssessment
from backend.app.models.nodes import Node
from backend.app.models.network import GatewayPacketLog
from backend.app.models.sensor_trust import SensorTrustLog
from backend.app.ai.risk_engine import risk_engine
from backend.app.services.alert_service import alert_service
from backend.app.websocket.manager import ws_manager
from backend.app.services.evidence_service import build_event_evidence
from backend.app.domain.registry import DOMAIN_REGISTRY
from backend.app.provenance import SourceMode, ValidationReason, resolve_source_mode
import time


class TelemetryService:
    """End-to-end ingest, AI assessment, persistence, and WebSocket broadcasting service."""

    # Track sequence numbers per node in-memory for immediate gap detection
    _last_sequence: Dict[str, int] = {}
    _packet_counters: Dict[str, Dict[str, int]] = {
        "JALA-01": {"total": 0, "lost": 0},
        "AGNI-02": {"total": 0, "lost": 0},
        "BHUMI-03": {"total": 0, "lost": 0},
    }

    def reset_sequence_tracking(self) -> None:
        """Reset volatile gateway counters for deterministic startup/tests."""
        self._last_sequence.clear()
        for counters in self._packet_counters.values():
            counters.update(total=0, lost=0)

    @staticmethod
    def _quarantined(node_id: str, sequence: int, source_mode: SourceMode, reason: ValidationReason) -> Dict[str, Any]:
        return {
            "status": "quarantined",
            "node_id": node_id,
            "sequence": sequence,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "risk_score": 0.0,
            "risk_band": "WITHHELD",
            "alerts_generated": 0,
            "sensor_trust": {},
            "source_mode": source_mode.value,
            "reason_code": reason.value,
        }

    async def ingest_packet(
        self,
        db: AsyncSession,
        payload: Dict[str, Any],
        gateway_source: str = "USB_SERIAL"
    ) -> Dict[str, Any]:
        """
        Validate, assess, persist, and broadcast incoming LoRa packet.
        """
        processing_started = time.perf_counter()
        node_id = payload.get("node_id")
        sequence = int(payload.get("sequence", 0))
        rssi = int(payload.get("rssi", -75))
        battery = float(payload.get("battery_pct", 100.0))
        metrics = payload.get("metrics", {})
        source_mode = resolve_source_mode(payload.get("source_mode"), payload.get("is_simulation"))
        is_simulation = source_mode is SourceMode.SIMULATION
        domain = DOMAIN_REGISTRY.get(node_id)
        if domain is None:
            return self._quarantined(node_id, sequence, source_mode, ValidationReason.INVALID_SCHEMA)
        if domain.default_source_mode is SourceMode.PLANNED or source_mode is SourceMode.PLANNED:
            return self._quarantined(node_id, sequence, source_mode, ValidationReason.PLANNED_NODE_TELEMETRY)
        if source_mode is SourceMode.EXTERNAL_DATA:
            return self._quarantined(node_id, sequence, source_mode, ValidationReason.INVALID_SOURCE_MODE)

        now_utc = datetime.now(timezone.utc)
        raw_device_timestamp = payload.get("timestamp")
        try:
            device_timestamp = datetime.fromisoformat(raw_device_timestamp.replace("Z", "+00:00")) if raw_device_timestamp else now_utc
            if device_timestamp.tzinfo is None:
                device_timestamp = device_timestamp.replace(tzinfo=timezone.utc)
            device_timestamp = device_timestamp.astimezone(timezone.utc)
        except (AttributeError, TypeError, ValueError):
            return self._quarantined(node_id, sequence, source_mode, ValidationReason.INVALID_SCHEMA)
        clock_drift_seconds = (now_utc - device_timestamp).total_seconds()
        if clock_drift_seconds < -300:
            return self._quarantined(node_id, sequence, source_mode, ValidationReason.FUTURE_TIMESTAMP)
        if clock_drift_seconds > 86400 and source_mode is not SourceMode.REPLAY:
            return self._quarantined(node_id, sequence, source_mode, ValidationReason.STALE_PACKET)

        # Check sequence gaps and duplicate detection
        last_seq = self._last_sequence.get(node_id)
        sequence_gap = 0
        is_duplicate = False

        if last_seq is not None:
            if sequence == last_seq:
                is_duplicate = True
            elif sequence > last_seq + 1:
                sequence_gap = sequence - (last_seq + 1)
                self._packet_counters.setdefault(node_id, {"total": 0, "lost": 0})["lost"] += sequence_gap
            elif sequence < last_seq and source_mode is not SourceMode.REPLAY:
                return self._quarantined(node_id, sequence, source_mode, ValidationReason.OUT_OF_ORDER)

        if is_duplicate:
            return {
                "status": "duplicate",
                "node_id": node_id,
                "sequence": sequence,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "risk_score": 0.0,
                "risk_band": "UNCHANGED",
                "alerts_generated": 0,
                "sensor_trust": {},
                "source_mode": source_mode.value,
                "reason_code": ValidationReason.DUPLICATE.value,
            }

        self._last_sequence[node_id] = sequence
        self._packet_counters.setdefault(node_id, {"total": 0, "lost": 0})["total"] += 1

        total_pkts = self._packet_counters[node_id]["total"]
        lost_pkts = self._packet_counters[node_id]["lost"]
        packet_loss_pct = round((lost_pkts / max(1, total_pkts + lost_pkts)) * 100.0, 1)

        # REPLAY records remain isolated from current risk, alert, and node state.
        if source_mode is SourceMode.REPLAY:
            db.add(TelemetryRecord(
                node_id=node_id, sequence=sequence, timestamp=device_timestamp,
                device_timestamp=device_timestamp, server_received_at=now_utc,
                rssi=rssi, battery_pct=battery, raw_payload=payload, metrics=metrics,
                is_simulation=0, source_mode=source_mode.value,
                gateway_id=payload.get("gateway_id"), transport=payload.get("transport") or gateway_source,
                clock_drift_seconds=clock_drift_seconds,
            ))
            await db.commit()
            return {
                "status": "stored_isolated", "node_id": node_id, "sequence": sequence,
                "processed_at": now_utc.isoformat(), "risk_score": 0.0, "risk_band": "UNCHANGED",
                "alerts_generated": 0, "sensor_trust": {}, "source_mode": source_mode.value,
                "reason_code": None,
            }

        # 1. Fetch recent telemetry history for dynamic derivatives and stuck checks
        hist_query = (
            select(TelemetryRecord.metrics)
            .where(TelemetryRecord.node_id == node_id)
            .order_by(desc(TelemetryRecord.timestamp))
            .limit(12)
        )
        hist_res = await db.execute(hist_query)
        recent_history = [row[0] for row in hist_res.all()]
        recent_history.reverse()  # Chronological order

        # 2. Run Hybrid Risk & Sensor Trust Engine
        assessment = risk_engine.evaluate_node(
            node_id=node_id,
            current_metrics=metrics,
            recent_history=recent_history,
            is_simulation=is_simulation
        )

        # 3. Save Telemetry Record
        telemetry_rec = TelemetryRecord(
            node_id=node_id,
            sequence=sequence,
            timestamp=device_timestamp,
            device_timestamp=device_timestamp,
            server_received_at=now_utc,
            rssi=rssi,
            battery_pct=battery,
            raw_payload=payload,
            metrics=metrics,
            is_simulation=1 if is_simulation else 0,
            source_mode=source_mode.value,
            gateway_id=payload.get("gateway_id"),
            transport=payload.get("transport") or gateway_source,
            clock_drift_seconds=clock_drift_seconds,
        )
        db.add(telemetry_rec)

        # 4. Save Risk Assessment
        risk_rec = RiskAssessment(
            node_id=node_id,
            timestamp=now_utc,
            risk_score=assessment["risk_score"],
            risk_band=assessment["risk_band"],
            confidence=assessment["confidence"],
            anomaly_score=assessment["anomaly_score"],
            sensor_trust=assessment["sensor_trust"],
            contributing_factors=assessment["contributing_factors"],
            human_explanation=assessment["human_explanation"],
            machine_explanation=assessment["machine_explanation"],
            recommended_action=assessment["recommended_action"],
            model_source=assessment["model_source"],
            estimated_crossing_time=assessment.get("estimated_crossing_time"),
            risk_trend=assessment.get("risk_trend", "STABLE")
        )
        db.add(risk_rec)

        # 5. Save Sensor Trust Logs
        for sensor_name, trust_val in assessment["sensor_trust"].items():
            db.add(SensorTrustLog(
                node_id=node_id,
                sensor_name=sensor_name,
                trust_score=trust_val,
                timestamp=now_utc
            ))

        # 6. Save Gateway Packet Log
        db.add(GatewayPacketLog(
            node_id=node_id,
            sequence=sequence,
            timestamp=now_utc,
            rssi=rssi,
            is_valid=True,
            is_duplicate=is_duplicate,
            sequence_gap=sequence_gap,
            gateway_source=gateway_source
        ))

        # 7. Update Node State
        node_query = select(Node).where(Node.id == node_id)
        node_res = await db.execute(node_query)
        node_obj = node_res.scalar_one_or_none()
        if node_obj and not (node_obj.source_mode == SourceMode.REAL.value and source_mode is not SourceMode.REAL):
            node_obj.last_seen = now_utc
            node_obj.battery_pct = battery
            node_obj.signal_rssi = rssi
            node_obj.packet_loss_pct = packet_loss_pct
            node_obj.source_mode = source_mode.value
            if assessment["risk_band"] == "CRITICAL":
                node_obj.status = "CRITICAL"
            elif assessment["risk_band"] == "WARNING":
                node_obj.status = "WARNING"
            elif assessment["risk_band"] == "WATCH":
                node_obj.status = "WATCH"
            else:
                node_obj.status = "ONLINE"

        # 8. Alert Lifecycle Evaluation
        evidence = build_event_evidence(
            event_id=f"EVT-{node_id}-{sequence}", node_id=node_id,
            hazard={"JALA-01": "FLOOD", "AGNI-02": "FIRE", "BHUMI-03": "LANDSLIDE"}.get(node_id, "HAZARD"),
            timestamp=now_utc.isoformat(), raw_telemetry=payload,
            processed_features={"contributors": assessment["contributing_factors"], "trend": assessment.get("risk_trend")},
            risk={"score": assessment["risk_score"], "band": assessment["risk_band"]},
            confidence=assessment["confidence"], sensor_trust=assessment["sensor_trust"],
            explanation=assessment["human_explanation"],
            gateway_state={"source": gateway_source, "rssi": rssi},
            network_state={"sequence_gap": sequence_gap, "packet_loss_pct": packet_loss_pct},
            processing_latency_ms=round((time.perf_counter() - processing_started) * 1000, 2),
        )
        evidence["provenance"] = {
            "source_mode": source_mode.value,
            "device_timestamp": device_timestamp.isoformat(),
            "server_received_at": now_utc.isoformat(),
            "gateway_id": payload.get("gateway_id"),
            "transport": payload.get("transport") or gateway_source,
        }
        alert_item = await alert_service.evaluate_and_create_alert(
            db=db,
            node_id=node_id,
            risk_score=assessment["risk_score"],
            risk_band=assessment["risk_band"],
            confidence=assessment["confidence"],
            explanation=assessment["human_explanation"],
            action_recommended=assessment["recommended_action"],
            evidence=evidence
        )

        await db.commit()

        # 9. Real-time WebSocket broadcasts
        await ws_manager.broadcast_event("telemetry.updated", {
            "node_id": node_id,
            "sequence": sequence,
            "timestamp": now_utc.isoformat(),
            "metrics": metrics,
            "rssi": rssi,
            "battery_pct": battery,
            "is_simulation": is_simulation
            ,"source_mode": source_mode.value
            ,"device_timestamp": device_timestamp.isoformat()
            ,"server_received_at": now_utc.isoformat()
        })

        await ws_manager.broadcast_event("risk.updated", {
            "node_id": node_id,
            "timestamp": now_utc.isoformat(),
            "risk_score": assessment["risk_score"],
            "risk_band": assessment["risk_band"],
            "confidence": assessment["confidence"],
            "anomaly_score": assessment["anomaly_score"],
            "sensor_trust": assessment["sensor_trust"],
            "contributing_factors": assessment["contributing_factors"],
            "human_explanation": assessment["human_explanation"],
            "recommended_action": assessment["recommended_action"],
            "model_source": assessment["model_source"],
            "estimated_crossing_time": assessment.get("estimated_crossing_time"),
            "risk_trend": assessment.get("risk_trend")
        })

        if node_obj:
            await ws_manager.broadcast_event("node.status_changed", {
                "node_id": node_id,
                "status": node_obj.status,
                "battery_pct": node_obj.battery_pct,
                "signal_rssi": node_obj.signal_rssi,
                "packet_loss_pct": node_obj.packet_loss_pct,
                "last_seen": node_obj.last_seen.isoformat()
            })

        await ws_manager.broadcast_event("sensor.trust_changed", {"node_id": node_id, "sensor_trust": assessment["sensor_trust"]})
        await ws_manager.broadcast_event("gateway.updated", {"status": "CONNECTED", "source": gateway_source, "last_packet_at": now_utc.isoformat()})
        await ws_manager.broadcast_event("network.updated", {"node_id": node_id, "rssi": rssi, "sequence_gap": sequence_gap, "packet_loss_pct": packet_loss_pct})

        return {
            "status": "success",
            "node_id": node_id,
            "sequence": sequence,
            "processed_at": now_utc.isoformat(),
            "risk_score": assessment["risk_score"],
            "risk_band": assessment["risk_band"],
            "alerts_generated": 1 if alert_item else 0,
            "sensor_trust": assessment["sensor_trust"]
            ,"source_mode": source_mode.value
            ,"reason_code": None
        }


telemetry_service = TelemetryService()
