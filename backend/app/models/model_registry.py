import uuid
from datetime import datetime,timezone
from sqlalchemy import DateTime,Float,Integer,JSON,String
from sqlalchemy.orm import Mapped,mapped_column
from backend.app.core.database import Base

class DatasetManifest(Base):
    __tablename__="dataset_manifests"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    name:Mapped[str]=mapped_column(String(128),index=True)
    version:Mapped[str|None]=mapped_column(String(64),nullable=True)
    checksum:Mapped[str|None]=mapped_column(String(128),nullable=True)
    provenance:Mapped[str]=mapped_column(String(32))
    validation_status:Mapped[str]=mapped_column(String(32),index=True)
    validation_errors:Mapped[list]=mapped_column(JSON,default=list)
    metadata_info:Mapped[dict]=mapped_column("metadata",JSON,default=dict)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))

class ModelArtifact(Base):
    __tablename__="model_artifacts"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    name:Mapped[str]=mapped_column(String(128),index=True)
    version:Mapped[str]=mapped_column(String(64))
    artifact_checksum:Mapped[str]=mapped_column(String(128))
    provenance:Mapped[str]=mapped_column(String(32),default="MODEL")
    validation_status:Mapped[str]=mapped_column(String(32),default="UNVALIDATED",index=True)
    validation_evidence:Mapped[dict]=mapped_column(JSON,default=dict)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))

class DriftAssessment(Base):
    __tablename__="model_drift_assessments"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    model_id:Mapped[str]=mapped_column(String(36),index=True)
    score:Mapped[float]=mapped_column(Float)
    threshold:Mapped[float]=mapped_column(Float)
    sample_count:Mapped[int]=mapped_column(Integer)
    state:Mapped[str]=mapped_column(String(32),index=True)
    assessed_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
