import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base

class InfrastructureAsset(Base):
    __tablename__="infrastructure_assets"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    external_id:Mapped[str]=mapped_column(String(100),unique=True,index=True)
    asset_type:Mapped[str]=mapped_column(String(50),index=True)
    geometry:Mapped[dict]=mapped_column(JSON)
    provenance:Mapped[str]=mapped_column(String(32),index=True)
    source_dataset_id:Mapped[str]=mapped_column(String(36),index=True)
    verified_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)

class InfrastructureDependency(Base):
    __tablename__="infrastructure_dependencies"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    upstream_asset_id:Mapped[str]=mapped_column(String(36),index=True)
    downstream_asset_id:Mapped[str]=mapped_column(String(36),index=True)
    dependency_type:Mapped[str]=mapped_column(String(50))
    provenance:Mapped[str]=mapped_column(String(32))
    evidence_refs:Mapped[list]=mapped_column(JSON,default=list)

class ImpactAssessment(Base):
    __tablename__="impact_assessments"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    status:Mapped[str]=mapped_column(String(32),index=True)
    population_exposed:Mapped[int|None]=mapped_column(Integer,nullable=True)
    assets_exposed:Mapped[int|None]=mapped_column(Integer,nullable=True)
    dependency_impacts:Mapped[list]=mapped_column(JSON,default=list)
    provenance:Mapped[str]=mapped_column(String(32),index=True)
    reason:Mapped[str]=mapped_column(Text)
    evaluated_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),index=True)

class EvacuationAssessment(Base):
    __tablename__="evacuation_assessments"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    status:Mapped[str]=mapped_column(String(32),index=True)
    route:Mapped[dict|None]=mapped_column(JSON,nullable=True)
    guaranteed_safe:Mapped[bool]=mapped_column(Boolean,default=False)
    safety_disclaimer:Mapped[str]=mapped_column(Text)
    reliability:Mapped[float|None]=mapped_column(Float,nullable=True)
    provenance:Mapped[str]=mapped_column(String(32),index=True)
    reason:Mapped[str]=mapped_column(Text)
    evaluated_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),index=True)

class SafeZoneAssessment(Base):
    __tablename__="safe_zone_assessments"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    external_id:Mapped[str]=mapped_column(String(100),index=True)
    geometry:Mapped[dict]=mapped_column(JSON)
    reliability:Mapped[float|None]=mapped_column(Float,nullable=True)
    status:Mapped[str]=mapped_column(String(32),index=True)
    provenance:Mapped[str]=mapped_column(String(32),index=True)
    limitations:Mapped[list]=mapped_column(JSON,default=list)
