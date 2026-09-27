import uuid
from datetime import datetime,timezone
from sqlalchemy import DateTime,JSON,String
from sqlalchemy.orm import Mapped,mapped_column
from backend.app.core.database import Base

class DisasterMemory(Base):
    __tablename__="disaster_memories"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    hazard:Mapped[str]=mapped_column(String(64),index=True)
    fingerprint:Mapped[str]=mapped_column(String(64),index=True)
    features:Mapped[dict]=mapped_column(JSON)
    evidence_ids:Mapped[list]=mapped_column(JSON)
    provenance:Mapped[str]=mapped_column(String(32),index=True)
    previous_hash:Mapped[str]=mapped_column(String(64))
    entry_hash:Mapped[str]=mapped_column(String(64),unique=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),index=True)
