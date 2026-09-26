from fastapi import APIRouter, Body, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.services.evidence_gate_service import evidence_gate_service
from backend.app.models.evidence_gate import EvidenceGateEvaluation


router = APIRouter(prefix="/evidence-gate", tags=["Evidence Gate"])


@router.post("/evaluate")
async def evaluate(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    return await evidence_gate_service.evaluate(db, payload)


@router.get("/evaluations")
async def evaluations(limit: int = 50, db: AsyncSession = Depends(get_db)):
    records = list((await db.execute(select(EvidenceGateEvaluation).order_by(desc(EvidenceGateEvaluation.created_at)).limit(min(max(limit, 1), 200)))).scalars())
    return [{"id": item.id, "hazard": item.hazard, "severity": item.severity,
             "lifecycle": item.lifecycle, "publication_allowed": item.publication_allowed,
             "confidence": item.confidence, "policy_version": item.policy_version,
             "checks": item.checks, "evidence_ids": item.evidence_ids,
             "why_withheld": item.why_withheld, "created_at": item.created_at} for item in records]
