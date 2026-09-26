import uuid
from datetime import datetime,timezone
from sqlalchemy import DateTime,Integer,JSON,String,Text
from sqlalchemy.orm import Mapped,mapped_column
from backend.app.core.database import Base
class OutboundQueueItem(Base):
    __tablename__="outbound_queue_items"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    checksum:Mapped[str]=mapped_column(String(64),unique=True,index=True)
    operation:Mapped[str]=mapped_column(String(64),index=True)
    body:Mapped[dict]=mapped_column(JSON)
    provenance:Mapped[str]=mapped_column(String(32),index=True)
    state:Mapped[str]=mapped_column(String(24),index=True,default="QUEUED")
    attempts:Mapped[int]=mapped_column(Integer,default=0)
    last_error:Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),index=True)
    acknowledged_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
class ContinuitySnapshot(Base):
    __tablename__="continuity_snapshots"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    mode:Mapped[str]=mapped_column(String(32),index=True)
    link_state:Mapped[dict]=mapped_column(JSON)
    energy_policy:Mapped[str]=mapped_column(String(24))
    network_policy:Mapped[str]=mapped_column(String(24))
    reason:Mapped[str]=mapped_column(Text)
    evaluated_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),index=True)
