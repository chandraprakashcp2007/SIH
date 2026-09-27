from fastapi import APIRouter,Body,Depends,HTTPException
from sqlalchemy import desc,select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.model_registry import DatasetManifest,DriftAssessment,ModelArtifact

router=APIRouter(prefix="/ml",tags=["Dataset and Model Registry"])
def row(x):return {c.name:getattr(x,"metadata_info" if c.name=="metadata" else c.name) for c in x.__table__.columns}

@router.get("/datasets")
async def datasets(db:AsyncSession=Depends(get_db)):
    return [row(x) for x in (await db.execute(select(DatasetManifest).order_by(desc(DatasetManifest.created_at)))).scalars()]

@router.post("/datasets")
async def validate_dataset(payload:dict=Body(...),db:AsyncSession=Depends(get_db)):
    errors=[field for field in ("checksum","version","license_reference") if not payload.get(field)]
    item=DatasetManifest(name=payload.get("name","unnamed"),version=payload.get("version"),checksum=payload.get("checksum"),provenance=payload.get("provenance","EXTERNAL_DATA"),validation_status="MANIFEST_COMPLETE_UNVERIFIED" if not errors else "INVALID",validation_errors=errors,metadata_info={**{k:v for k,v in payload.items() if k not in {"name","version","checksum","provenance"}},"validation_authority":"NOT_CONFIGURED"})
    db.add(item);await db.commit();return row(item)

@router.get("/models")
async def models(db:AsyncSession=Depends(get_db)):
    return [row(x) for x in (await db.execute(select(ModelArtifact).order_by(desc(ModelArtifact.created_at)))).scalars()]

@router.post("/models")
async def register_model(payload:dict=Body(...),db:AsyncSession=Depends(get_db)):
    evidence=payload.get("validation_evidence") or {}
    status="UNVALIDATED"
    item=ModelArtifact(name=payload.get("name","unnamed"),version=payload.get("version","unversioned"),artifact_checksum=payload.get("artifact_checksum",""),provenance="MODEL",validation_status=status,validation_evidence=evidence)
    db.add(item);await db.commit();return row(item)

@router.post("/models/{model_id}/drift")
async def record_drift(model_id:str,payload:dict=Body(...),db:AsyncSession=Depends(get_db)):
    if not await db.get(ModelArtifact,model_id):raise HTTPException(404,"MODEL_NOT_FOUND")
    score=float(payload.get("score",0));threshold=float(payload.get("threshold",0));samples=int(payload.get("sample_count",0))
    state="INSUFFICIENT_DATA" if samples<10 else "OUT_OF_DISTRIBUTION" if score>threshold else "IN_DISTRIBUTION"
    item=DriftAssessment(model_id=model_id,score=score,threshold=threshold,sample_count=samples,state=state);db.add(item);await db.commit();return row(item)

@router.post("/models/{model_id}/evaluate")
async def evaluate(model_id:str,db:AsyncSession=Depends(get_db)):
    model=await db.get(ModelArtifact,model_id)
    if not model:raise HTTPException(404,"MODEL_NOT_FOUND")
    if model.validation_status!="VALIDATED":return {"decision":"ABSTAIN","reason":"MODEL_NOT_VALIDATED","model_id":model.id,"evidence_ids":[]}
    drift=(await db.execute(select(DriftAssessment).where(DriftAssessment.model_id==model_id).order_by(desc(DriftAssessment.assessed_at)).limit(1))).scalar_one_or_none()
    if drift and drift.state!="IN_DISTRIBUTION":return {"decision":"ABSTAIN","reason":drift.state,"model_id":model.id,"evidence_ids":[drift.id]}
    return {"decision":"ABSTAIN","reason":"NO_VERIFIED_EXECUTION_ADAPTER","model_id":model.id,"evidence_ids":[]}
