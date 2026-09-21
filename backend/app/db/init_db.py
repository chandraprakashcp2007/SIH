"""
PRAHARI-NET Database Initialization & Demo Seeder
Initializes SQLite schema, registers default credentials, and populates 3 core sensor nodes.
"""
import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from backend.app.core.database import engine, Base, AsyncSessionLocal
from backend.app.models.users import User
from backend.app.models.nodes import Node
from backend.app.models.telemetry import TelemetryRecord
from backend.app.models.risk import RiskAssessment
from backend.app.models.alerts import Alert
from backend.app.models.audit import AuditLog
from backend.app.models.copilot import ChatSession, ChatMessage, CopilotToolCall, CopilotFeedback, CopilotMetric
from backend.app.core.security import hash_password


async def init_models():
    """Create all database tables using async engine."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_data():
    """Seed initial users, nodes, and nominal telemetry history."""
    await init_models()

    async with AsyncSessionLocal() as db:
        # 1. Seed Users
        user_check = await db.execute(select(User).where(User.username == "admin"))
        if not user_check.scalar_one_or_none():
            users = [
                User(
                    username="admin",
                    email="admin@prahari.gov.in",
                    hashed_password=hash_password("prahari2026!"),
                    full_name="Col. R. Sharma (EOC Director)",
                    role="ADMIN"
                ),
                User(
                    username="operator",
                    email="operator@prahari.gov.in",
                    hashed_password=hash_password("prahari2026!"),
                    full_name="Duty Officer S. Verma",
                    role="OPERATOR"
                ),
                User(
                    username="viewer",
                    email="viewer@prahari.gov.in",
                    hashed_password=hash_password("prahari2026!"),
                    full_name="District Liaison Observer",
                    role="VIEWER"
                )
            ]
            db.add_all(users)

        # 2. Seed Nodes
        nodes = [
            Node(
                id="JALA-01",
                name="Brahmaputra Flood Intelligence",
                node_type="FLOOD",
                tagline="River Hydrodynamics & Surge Forecasting",
                latitude=26.1850,
                longitude=91.7539,
                elevation_m=55.0,
                location_name="Brahmaputra Basin - Sector 4",
                status="ONLINE",
                firmware_version="v1.4.2-lora",
                hardware_rev="SX1276-ESP32-RevB",
                battery_pct=94.0,
                solar_voltage=4.15,
                signal_rssi=-76,
                packet_loss_pct=0.2,
                sensors_configured=["water_level_ultrasonic", "tipping_rain_gauge", "dht22_ambient"],
                metadata_info={"channel_width_m": 450, "flood_warning_level_cm": 120}
            ),
            Node(
                id="AGNI-02",
                name="Similipal Forest Fire Node",
                node_type="FIRE",
                tagline="Atmospheric Combustion & Plume AI",
                latitude=21.8485,
                longitude=86.4250,
                elevation_m=420.0,
                location_name="Similipal Forest Perimeter - Ridge A",
                status="ONLINE",
                firmware_version="v1.4.2-lora",
                hardware_rev="SX1276-ESP32-RevB",
                battery_pct=91.0,
                solar_voltage=4.08,
                signal_rssi=-81,
                packet_loss_pct=0.5,
                sensors_configured=["mq2_smoke", "mq135_gas", "optical_flame_ir", "thermal_probe"],
                metadata_info={"coverage_radius_km": 3.5, "vegetation_type": "Dry Deciduous"}
            ),
            Node(
                id="BHUMI-03",
                name="NH-58 Landslide Inclinometer",
                node_type="LANDSLIDE",
                tagline="Pore Pressure & Slope Shear Dynamics",
                latitude=30.1450,
                longitude=78.3050,
                elevation_m=1150.0,
                location_name="NH-58 Ghat Section Km 42",
                status="ONLINE",
                firmware_version="v1.4.2-lora",
                hardware_rev="SX1276-ESP32-RevB",
                battery_pct=88.0,
                solar_voltage=3.95,
                signal_rssi=-84,
                packet_loss_pct=0.8,
                sensors_configured=["soil_moisture_tws_upper", "soil_moisture_tws_lower", "mpu6050_inclinometer", "geophone_vib"],
                metadata_info={"slope_angle_deg": 38.5, "lithology": "Fissured Shale / Quartzite"}
            )
        ]

        for n in nodes:
            existing = await db.execute(select(Node).where(Node.id == n.id))
            if not existing.scalar_one_or_none():
                db.add(n)

        # 3. Seed historical nominal records if empty
        t_check = await db.execute(select(TelemetryRecord).limit(1))
        if not t_check.scalar_one_or_none():
            now = datetime.now(timezone.utc)
            for i in range(20, 0, -1):
                past_time = now - timedelta(minutes=i * 2)

                # JALA nominal
                db.add(TelemetryRecord(
                    node_id="JALA-01",
                    sequence=100 - i,
                    timestamp=past_time,
                    rssi=-76,
                    battery_pct=94.0,
                    raw_payload={"demo": True},
                    metrics={"water_level_cm": 34.0 + (i % 3) * 0.4, "water_rise_rate_cm_min": 0.0, "rain_intensity": 0.0, "temperature_c": 28.2},
                    is_simulation=1
                ))
                db.add(RiskAssessment(
                    node_id="JALA-01",
                    timestamp=past_time,
                    risk_score=12.0,
                    risk_band="NORMAL",
                    confidence=95.0,
                    anomaly_score=0.02,
                    sensor_trust={"water_level_sensor": 98.0, "rain_sensor": 96.0},
                    contributing_factors=[],
                    human_explanation="Water levels and precipitation conform to normal hydrological baseline.",
                    machine_explanation={},
                    recommended_action="Normal routine hydrological surveillance.",
                    model_source="RULE_FUSION",
                    risk_trend="STABLE"
                ))

                # AGNI nominal
                db.add(TelemetryRecord(
                    node_id="AGNI-02",
                    sequence=100 - i,
                    timestamp=past_time,
                    rssi=-81,
                    battery_pct=91.0,
                    raw_payload={"demo": True},
                    metrics={"mq2_raw": 115.0 + (i % 4), "mq135_raw": 128.0, "temperature_c": 27.2, "flame_detected": False, "camera_fire_confidence": 0.0},
                    is_simulation=1
                ))
                db.add(RiskAssessment(
                    node_id="AGNI-02",
                    timestamp=past_time,
                    risk_score=8.0,
                    risk_band="NORMAL",
                    confidence=96.0,
                    anomaly_score=0.01,
                    sensor_trust={"mq2_smoke_sensor": 98.0, "thermal_sensor": 99.0},
                    contributing_factors=[],
                    human_explanation="Air quality, infrared radiation, and temperature match ambient environmental baseline.",
                    machine_explanation={},
                    recommended_action="Normal atmospheric monitoring.",
                    model_source="RULE_FUSION",
                    risk_trend="STABLE"
                ))

                # BHUMI nominal
                db.add(TelemetryRecord(
                    node_id="BHUMI-03",
                    sequence=100 - i,
                    timestamp=past_time,
                    rssi=-84,
                    battery_pct=88.0,
                    raw_payload={"demo": True},
                    metrics={"soil_moisture_upper_pct": 28.5 + (i % 2), "tilt_delta_deg": 0.12, "vibration_rms": 0.45, "rain_context": 5.0},
                    is_simulation=1
                ))
                db.add(RiskAssessment(
                    node_id="BHUMI-03",
                    timestamp=past_time,
                    risk_score=9.0,
                    risk_band="NORMAL",
                    confidence=94.0,
                    anomaly_score=0.02,
                    sensor_trust={"soil_moisture_upper": 97.0, "inclinometer_tilt": 98.0},
                    contributing_factors=[],
                    human_explanation="Slope inclination, geophone vibrations, and soil moisture remain in stable geological equilibrium.",
                    machine_explanation={},
                    recommended_action="Normal geotechnical slope stability.",
                    model_source="RULE_FUSION",
                    risk_trend="STABLE"
                ))

        # Initial Audit Log
        db.add(AuditLog(
            action="SYSTEM_INITIALIZED",
            category="AUTH",
            component="database_init",
            message="Database schema initialized and baseline demo nodes verified."
        ))

        await db.commit()
        print("PRAHARI-NET database successfully initialized with demo seed data.")


if __name__ == "__main__":
    asyncio.run(seed_data())
