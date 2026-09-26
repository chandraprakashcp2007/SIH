import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base

class DigitalTwinSnapshot(Base):
    __tablename__="digital_twin_snapshots"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    node_id: Mapped[str]=mapped_column(String(32),index=True)
    observed_location: Mapped[dict]=mapped_column(JSON)
    hazard_boundary: Mapped[dict|None]=mapped_column(JSON,nullable=True)
    uncertainty_boundary: Mapped[dict|None]=mapped_column(JSON,nullable=True)
    confidence: Mapped[float]=mapped_column(Float)
    uncertainty: Mapped[float]=mapped_column(Float)
    blind_spots: Mapped[list]=mapped_column(JSON)
    provenance: Mapped[str]=mapped_column(String(32),index=True)
    boundary_state: Mapped[str]=mapped_column(String(32))
    explanation: Mapped[str]=mapped_column(Text)
    captured_at: Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),index=True)
