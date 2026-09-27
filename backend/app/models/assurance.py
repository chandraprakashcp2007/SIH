import uuid
from datetime import datetime,timezone
from sqlalchemy import DateTime,Float,JSON,String
from sqlalchemy.orm import Mapped,mapped_column
from backend.app.core.database import Base
class AssuranceSnapshot(Base):
    __tablename__="assurance_snapshots"
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()));ddqi:Mapped[float]=mapped_column(Float);status:Mapped[str]=mapped_column(String(32),index=True);dimensions:Mapped[dict]=mapped_column(JSON);blockers:Mapped[list]=mapped_column(JSON);created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
