import uuid
from datetime import datetime,timezone
from sqlalchemy import DateTime,Integer,JSON,String
from sqlalchemy.orm import Mapped,mapped_column
from backend.app.core.database import Base
class LaboratoryRun(Base):
    __tablename__="laboratory_runs"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    kind:Mapped[str]=mapped_column(String(16),index=True)
    name:Mapped[str]=mapped_column(String(128))
    seed:Mapped[int]=mapped_column(Integer)
    inputs:Mapped[dict]=mapped_column(JSON)
    result_digest:Mapped[str]=mapped_column(String(64),index=True)
    provenance:Mapped[str]=mapped_column(String(32),default="SIMULATION")
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
