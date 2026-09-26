from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.evidence_gate import EvidenceGateEvaluation, EvidenceItem


CHECK_NAMES = (
    "packet validity", "provenance validity", "freshness", "physical plausibility",
    "sensor trust", "persistence", "hazard momentum", "multi-sensor agreement",
    "regional consensus", "authoritative external corroboration",
    "terrain/susceptibility evidence", "validated model availability",
    "uncertainty/calibration", "rule/model agreement", "counterfactual robustness",
)

POLICIES = {
    "WATCH": {"required": {1, 2, 3, 4, 5, 6}, "min_trust": .60, "max_staleness": 900},
    "WARNING": {"required": {1, 2, 3, 4, 5, 6, 8, 9, 13}, "min_trust": .70, "max_staleness": 600},
    "CRITICAL": {"required": {1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 15}, "min_trust": .80, "max_staleness": 300},
}


def _status(condition: bool | None) -> str:
    return "UNAVAILABLE" if condition is None else ("PASSED" if condition else "FAILED")


class EvidenceGateService:
    async def evaluate(self, db: AsyncSession, payload: dict) -> dict:
        severity = payload["severity"].upper()
        policy = POLICIES.get(severity, POLICIES["WARNING"])
        operational = payload.get("operational_provenance", "REAL")
        records = []
        for raw in payload.get("evidence", []):
            item = EvidenceItem(
                hazard=raw["hazard"], source=raw["source"], provider=raw["provider"],
                provenance=raw["provenance"], timestamp=datetime.now(timezone.utc),
                freshness_seconds=raw.get("freshness_seconds", 10**9), quality=raw.get("quality", 0),
                trust=raw.get("trust", 0), spatial_relevance=raw.get("spatial_relevance", 0),
                temporal_relevance=raw.get("temporal_relevance", 0), claim=raw.get("claim", {}),
                metadata_info=raw.get("metadata", {}),
            )
            db.add(item); records.append(item)
        await db.flush()
        metadata = [item.metadata_info for item in records]
        provenances = {item.provenance for item in records}
        max_age = max((item.freshness_seconds for item in records), default=10**9)
        avg_trust = sum((item.trust for item in records), 0.0) / len(records) if records else 0
        facts: dict[int, bool | None] = {
            1: bool(records) and all(m.get("packet_valid") is True for m in metadata),
            2: bool(records) and (operational != "REAL" or provenances <= {"REAL", "EXTERNAL_DATA", "MODEL"}),
            3: bool(records) and max_age <= policy["max_staleness"],
            4: bool(records) and all(m.get("physically_plausible") is True for m in metadata),
            5: avg_trust >= policy["min_trust"],
            6: bool(records) and any(m.get("persistent") is True for m in metadata),
            7: True if any(m.get("momentum") is True for m in metadata) else None,
            8: True if any(m.get("multi_sensor_agreement") is True for m in metadata) else None,
            9: True if any(m.get("regional_consensus") is True for m in metadata) else None,
            10: True if any(item.provenance == "EXTERNAL_DATA" and item.metadata_info.get("authoritative") for item in records) else None,
            11: True if any(m.get("terrain_evidence") for m in metadata) else None,
            12: True if any(item.provenance == "MODEL" and item.metadata_info.get("validated_model") for item in records) else None,
            13: True if any(m.get("calibrated_uncertainty") for m in metadata) else None,
            14: True if any(m.get("rule_model_agreement") for m in metadata) else None,
            15: True if any(m.get("counterfactual_robust") for m in metadata) else None,
        }
        checks = [{"number": number, "name": name, "status": _status(facts[number]),
                   "required": number in policy["required"], "optional": number not in policy["required"]}
                  for number, name in enumerate(CHECK_NAMES, 1)]
        failed_required = [item for item in checks if item["required"] and item["status"] != "PASSED"]
        freshness_weight = max(0.0, 1.0 - max_age / max(policy["max_staleness"], 1))
        quality = sum((item.quality for item in records), 0.0) / len(records) if records else 0
        confidence = round(100 * avg_trust * quality * freshness_weight, 2)
        lifecycle = "PUBLISHED" if not failed_required else "WITHHELD"
        evaluation = EvidenceGateEvaluation(
            hazard=payload["hazard"], severity=severity, lifecycle=lifecycle,
            publication_allowed=not failed_required, confidence=confidence,
            policy_version="gate-v1", checks=checks, evidence_ids=[item.id for item in records],
            why_withheld=[f"Check {item['number']:02d} {item['name']}: {item['status']}" for item in failed_required],
        )
        db.add(evaluation); await db.commit()
        return {"id": evaluation.id, "hazard": evaluation.hazard, "severity": severity,
                "lifecycle": lifecycle, "publication_allowed": not failed_required,
                "confidence": confidence, "policy_version": evaluation.policy_version,
                "checks": checks, "evidence_ids": evaluation.evidence_ids,
                "why_withheld": evaluation.why_withheld}


evidence_gate_service = EvidenceGateService()
