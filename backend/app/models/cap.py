import uuid
from datetime import datetime,timezone
from sqlalchemy import DateTime,JSON,String,Text
from sqlalchemy.orm import Mapped,mapped_column
from backend.app.core.database import Base
class CAPExport(Base):
    __tablename__="cap_exports"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    alert_id:Mapped[str]=mapped_column(String(36),index=True)
    identifier:Mapped[str]=mapped_column(String(128),unique=True,index=True)
    lifecycle:Mapped[str]=mapped_column(String(20))
    languages:Mapped[list]=mapped_column(JSON)
    xml:Mapped[str]=mapped_column(Text)
    provenance:Mapped[str]=mapped_column(String(32),index=True)
    validation_state:Mapped[str]=mapped_column(String(20))
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),index=True)
class DeliveryAttempt(Base):
    __tablename__="delivery_attempts"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    alert_id:Mapped[str]=mapped_column(String(36),index=True)
    channel:Mapped[str]=mapped_column(String(32),index=True)
    state:Mapped[str]=mapped_column(String(32),index=True)
    provider_message_id:Mapped[str|None]=mapped_column(String(128),nullable=True)
    reason:Mapped[str]=mapped_column(Text)
    requested_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),index=True)
    delivered_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
