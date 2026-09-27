import uuid
from datetime import datetime,timezone
from sqlalchemy import Boolean,DateTime,JSON,String,Text
from sqlalchemy.orm import Mapped,mapped_column
from backend.app.core.database import Base
class DamageEvidence(Base):
    __tablename__="damage_evidence"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    incident_id:Mapped[str]=mapped_column(String(64),index=True);kind:Mapped[str]=mapped_column(String(64));provenance:Mapped[str]=mapped_column(String(32));description:Mapped[str]=mapped_column(Text);artifact_reference:Mapped[str|None]=mapped_column(String(256),nullable=True);human_verified:Mapped[bool]=mapped_column(Boolean,default=False);verified_by:Mapped[str|None]=mapped_column(String(64),nullable=True);verified_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True);verification_state:Mapped[str]=mapped_column(String(40));created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
class RecoveryReport(Base):
    __tablename__="recovery_reports"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()));incident_id:Mapped[str]=mapped_column(String(64),index=True);evidence_ids:Mapped[list]=mapped_column(JSON);provenance:Mapped[str]=mapped_column(String(32));recovery_status:Mapped[str]=mapped_column(String(40));auto_all_clear:Mapped[bool]=mapped_column(Boolean,default=False);narrative:Mapped[str]=mapped_column(Text);created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
