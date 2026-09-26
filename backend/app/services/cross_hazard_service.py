"""Cross-domain reevaluation without unsupported physical-causation claims."""
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.cross_hazard import (
    CompoundRiskAssessment, ConsensusAssessment, CrossHazardRelationship,
)
from backend.app.models.risk import RiskAssessment
from backend.app.models.telemetry import TelemetryRecord


RELATIONSHIPS = (
    ("AKASHA-05", "JALA-01", "Heavy-weather observations require flood-domain reevaluation."),
    ("AKASHA-05", "BHUMI-03", "Heavy-weather observations require slope-domain reevaluation."),
    ("AGNI-02", "VAYU-04", "Fire and smoke observations require air-domain reevaluation."),
    ("JALA-01", "BHUMI-03", "Flood observations require terrain-access reevaluation."),
)
COMPOUND_RULES = (
    ("FLOOD_LANDSLIDE_V1", ("JALA-01", "BHUMI-03"), "Flood and slope warning bands are jointly active."),
    ("FIRE_AIR_V1", ("AGNI-02", "VAYU-04"), "Fire and air-quality warning bands are jointly active."),
    ("WEATHER_FLOOD_V1", ("AKASHA-05", "JALA-01"), "Weather and flood warning bands are jointly active."),
)
NODES = ("JALA-01", "AGNI-02", "BHUMI-03", "VAYU-04", "AKASHA-05")
ACTIVE = {"WATCH", "WARNING", "CRITICAL"}


async def _latest(db: AsyncSession, model, node_id: str):
    return (await db.execute(select(model).where(model.node_id == node_id).order_by(desc(model.timestamp)).limit(1))).scalar_one_or_none()


def _source_mode(telemetry: TelemetryRecord | None) -> str:
    value = telemetry.source_mode if telemetry else "SIMULATION"
    return value if value in {"REAL", "SIMULATION", "EXTERNAL_DATA", "MODEL"} else "SIMULATION"


def _row(item):
    return {column.name: getattr(item, column.name) for column in item.__table__.columns}


class CrossHazardService:
    async def reevaluate(self, db: AsyncSession) -> dict:
        risks = {node: await _latest(db, RiskAssessment, node) for node in NODES}
        telemetry = {node: await _latest(db, TelemetryRecord, node) for node in NODES}
        relationships = []
        for source, target, explanation in RELATIONSHIPS:
            source_band = risks[source].risk_band if risks[source] else "UNKNOWN"
            target_band = risks[target].risk_band if risks[target] else "UNKNOWN"
            record = CrossHazardRelationship(
                source_node_id=source, target_node_id=target,
                state="REEVALUATION_REQUIRED" if source_band in ACTIVE else "MONITORING",
                source_risk_band=source_band, target_risk_band=target_band,
                confidence=min(risks[source].confidence, risks[target].confidence) if risks[source] and risks[target] else 0.0,
                provenance=_source_mode(telemetry[source]),
                evidence_refs=[r.id for r in (risks[source], risks[target]) if r], explanation=explanation,
            )
            db.add(record)
            relationships.append(record)

        compounds = []
        rank = {"UNKNOWN": 0, "NORMAL": 1, "WATCH": 2, "WARNING": 3, "CRITICAL": 4}
        for rule_id, participants, active_explanation in COMPOUND_RULES:
            bands = [risks[node].risk_band if risks[node] else "UNKNOWN" for node in participants]
            active_count = len([band for band in bands if band in ACTIVE])
            risk_class = "COMPOUND_WARNING" if active_count == len(participants) else "MONITORING"
            confidence = min((risks[node].confidence for node in participants if risks[node]), default=0.0)
            provenance = "SIMULATION" if any(_source_mode(telemetry[node]) == "SIMULATION" for node in participants) else _source_mode(telemetry[participants[0]])
            explanation = active_explanation if risk_class == "COMPOUND_WARNING" else f"Rule not active; participant bands are {', '.join(bands)}."
            record = CompoundRiskAssessment(
                rule_id=rule_id, rule_version="1.0", participants=list(participants), risk_class=risk_class,
                confidence=confidence, uncertainty=round(100.0 - confidence, 2), provenance=provenance,
                evidence_refs=[risks[node].id for node in participants if risks[node]], explanation=explanation,
            )
            db.add(record)
            compounds.append(record)

        consensus = []
        for node in NODES:
            record = ConsensusAssessment(
                node_id=node, state="INSUFFICIENT_NEIGHBOURS", neighbour_count=0, required_neighbours=2,
                weights={"trust": "READY", "freshness": "READY", "distance": "READY", "quality": "READY"},
                provenance=_source_mode(telemetry[node]),
                explanation="No independently configured neighbouring nodes are available; no consensus value was produced.",
            )
            db.add(record)
            consensus.append(record)
        await db.commit()
        return {
            "relationships": [_row(item) for item in relationships],
            "compound_risks": [_row(item) for item in compounds],
            "consensus": [_row(item) for item in consensus],
            "evaluated_at": datetime.now(timezone.utc),
        }


cross_hazard_service = CrossHazardService()
