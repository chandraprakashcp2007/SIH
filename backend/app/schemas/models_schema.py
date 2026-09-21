"""
Pydantic Schemas for Risk Assessments, Alerts, and Nodes
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# --- Risk Schemas ---
class FactorWeight(BaseModel):
    factor: str
    weight: float
    value: Any


class ExplanationSchema(BaseModel):
    human_readable: str
    machine_readable: Dict[str, Any]


class RiskAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    node_id: str
    timestamp: datetime
    risk_score: float
    risk_band: str
    confidence: float
    anomaly_score: float
    sensor_trust: Dict[str, float]
    contributing_factors: List[Dict[str, Any]]
    human_explanation: str
    machine_explanation: Dict[str, Any]
    recommended_action: str
    model_source: str
    estimated_crossing_time: Optional[str] = None
    risk_trend: Optional[str] = "STABLE"

class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    severity: str
    hazard: str
    node_id: str
    location_name: str
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    state: str
    confidence: float
    risk_score: float
    headline: str
    summary: str
    action_recommended: str
    evidence: Dict[str, Any]
    resolution_notes: Optional[str] = None


class AlertAcknowledgeRequest(BaseModel):
    acknowledged_by: Optional[str] = "operator"
    notes: Optional[str] = None


class AlertResolveRequest(BaseModel):
    resolved_by: Optional[str] = "operator"
    resolution_notes: str = Field(..., min_length=3, description="Operational notes detailing resolution")


# --- Node Schemas ---
class NodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    node_type: str
    tagline: Optional[str] = None
    latitude: float
    longitude: float
    elevation_m: float
    location_name: str
    status: str
    firmware_version: str
    hardware_rev: str
    battery_pct: float
    solar_voltage: float
    signal_rssi: int
    packet_loss_pct: float
    last_seen: datetime
    sensors_configured: List[str]
    metadata_info: Dict[str, Any]
    latest_risk: Optional[RiskAssessmentResponse] = None
    latest_metrics: Optional[Dict[str, Any]] = None


# --- Auth Schemas ---
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
