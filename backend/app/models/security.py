import uuid
from datetime import datetime,timezone
from sqlalchemy import DateTime,JSON,String,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from backend.app.core.database import Base
class TelemetryNonce(Base):
    __tablename__="telemetry_nonces"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    node_id:Mapped[str]=mapped_column(String(32),index=True)
    nonce:Mapped[str]=mapped_column(String(128))
    signature_fingerprint:Mapped[str]=mapped_column(String(64))
    accepted_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),index=True)
    __table_args__=(UniqueConstraint("node_id","nonce",name="uq_telemetry_node_nonce"),)
class SecurityEvent(Base):
    __tablename__="security_events"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    event_type:Mapped[str]=mapped_column(String(64),index=True)
    severity:Mapped[str]=mapped_column(String(16),index=True)
    node_id:Mapped[str|None]=mapped_column(String(32),nullable=True,index=True)
    details:Mapped[dict]=mapped_column(JSON,default=dict)
    previous_hash:Mapped[str]=mapped_column(String(64))
    event_hash:Mapped[str]=mapped_column(String(64),unique=True,index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),index=True)
