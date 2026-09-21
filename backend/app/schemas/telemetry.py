"""
Pydantic Schemas for Telemetry Payloads & Responses
"""
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TelemetryIngestPayload(BaseModel):
    version: int = Field(1, description="Protocol version number")
    node_id: str = Field(..., description="Target node ID: JALA-01, AGNI-02, BHUMI-03")
    sequence: int = Field(..., ge=0, description="Monotonically increasing sequence number")
    timestamp: Optional[str] = Field(None, description="ISO-8601 timestamp")
    metrics: Dict[str, Any] = Field(..., description="Node sensor telemetry key-values")
    rssi: int = Field(-75, ge=-140, le=-10, description="Received Signal Strength Indication")
    battery_pct: Optional[float] = Field(100.0, ge=0.0, le=100.0, description="Battery level percentage")
    is_simulation: Optional[bool] = Field(False, description="Flag indicating simulated telemetry")


class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    node_id: str
    sequence: int
    timestamp: datetime
    rssi: int
    battery_pct: float
    metrics: Dict[str, Any]
    is_simulation: int


class IngestResponse(BaseModel):
    status: str = "success"
    node_id: str
    sequence: int
    processed_at: str
    risk_score: float
    risk_band: str
    alerts_generated: int
    sensor_trust: Dict[str, float]
