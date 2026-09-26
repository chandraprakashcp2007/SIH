"""
PRAHARI-NET Database Initialization & Demo Seeder
Initializes SQLite schema, registers default credentials, and populates 3 core sensor nodes.
"""
import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, text
from backend.app.core.database import engine, Base, AsyncSessionLocal
from backend.app.models.users import User
from backend.app.models.nodes import Node
from backend.app.models.telemetry import TelemetryRecord
from backend.app.models.risk import RiskAssessment
from backend.app.models.alerts import Alert
from backend.app.models.audit import AuditLog
from backend.app.models.copilot import ChatSession, ChatMessage, CopilotToolCall, CopilotFeedback, CopilotMetric
from backend.app.core.security import hash_password
from backend.app.domain.registry import DOMAIN_REGISTRY


async def init_models():
    """Create all database tables using async engine."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if conn.dialect.name == "sqlite":
            migrations = {
                "telemetry_records": {
                    "device_timestamp": "DATETIME",
                    "server_received_at": "DATETIME",
                    "source_mode": "VARCHAR(32) NOT NULL DEFAULT 'SIMULATION'",
                    "gateway_id": "VARCHAR(64)",
                    "transport": "VARCHAR(32)",
                    "clock_drift_seconds": "FLOAT NOT NULL DEFAULT 0.0",
                },
                "nodes": {
                    "source_mode": "VARCHAR(32) NOT NULL DEFAULT 'SIMULATION'",
                    "hardware_profile": "JSON",
                },
            }
            for table_name, columns in migrations.items():
                existing = {row[1] for row in (await conn.execute(text(f"PRAGMA table_info({table_name})"))).all()}
                for column_name, definition in columns.items():
                    if column_name not in existing:
                        await conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"))
            await conn.execute(text(
                "UPDATE telemetry_records SET device_timestamp = timestamp WHERE device_timestamp IS NULL"
            ))
            await conn.execute(text(
                "UPDATE telemetry_records SET server_received_at = timestamp WHERE server_received_at IS NULL"
            ))


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
                latitude=26.1445,
                longitude=91.7362,
                elevation_m=0.0,
                location_name="SIMULATION DEMO LOCATION - NOT FIELD DEPLOYED",
                status="SIMULATION",
                firmware_version="ESP8266-PROTOTYPE",
                hardware_rev="NodeMCU ESP8266 BENCH PROTOTYPE",
                battery_pct=94.0,
                solar_voltage=0.0,
                signal_rssi=-76,
                packet_loss_pct=0.2,
                sensors_configured=["water_level_ultrasonic", "tipping_rain_gauge", "dht11_ambient"],
                metadata_info={"demo_location": True, "physical_location_verified": False, "flood_warning_level_cm": 120}
                ,source_mode="SIMULATION"
            ),
            Node(
                id="AGNI-02",
                name="Similipal Forest Fire Node",
                node_type="FIRE",
                tagline="Atmospheric Combustion & Plume AI",
                latitude=21.9497,
                longitude=86.72,
                elevation_m=0.0,
                location_name="SIMULATION DEMO LOCATION - NOT FIELD DEPLOYED",
                status="SIMULATION",
                firmware_version="PLANNED",
                hardware_rev="ESP32 FIELD NODE - PLANNED",
                battery_pct=91.0,
                solar_voltage=0.0,
                signal_rssi=-81,
                packet_loss_pct=0.5,
                sensors_configured=["mq2_smoke", "mq135_gas", "optical_flame_ir", "thermal_probe"],
                metadata_info={"demo_location": True, "physical_location_verified": False}
                ,source_mode="SIMULATION"
            ),
            Node(
                id="BHUMI-03",
                name="NH-58 Landslide Inclinometer",
                node_type="LANDSLIDE",
                tagline="Pore Pressure & Slope Shear Dynamics",
                latitude=30.3165,
                longitude=78.0322,
                elevation_m=0.0,
                location_name="SIMULATION DEMO LOCATION - NOT FIELD DEPLOYED",
                status="SIMULATION",
                firmware_version="PLANNED",
                hardware_rev="ESP32 FIELD NODE - PLANNED",
                battery_pct=88.0,
                solar_voltage=0.0,
                signal_rssi=-84,
                packet_loss_pct=0.8,
                sensors_configured=["soil_moisture_tws_upper", "soil_moisture_tws_lower", "mpu6050_inclinometer", "geophone_vib"],
                metadata_info={"demo_location": True, "physical_location_verified": False}
                ,source_mode="SIMULATION"
            )
            ,
            Node(
                id="VAYU-04",
                name="VAYU Air Intelligence",
                node_type="AIR_QUALITY",
                tagline="Air Quality & Hazardous Gas Intelligence",
                latitude=28.6139,
                longitude=77.209,
                elevation_m=0.0,
                location_name="SIMULATION DEMO LOCATION - NOT FIELD DEPLOYED",
                status="SIMULATION",
                firmware_version="SOFTWARE-DOMAIN",
                hardware_rev="ESP32 AIR NODE - HARDWARE NOT CONNECTED",
                battery_pct=93.0,
                solar_voltage=0.0,
                signal_rssi=-82,
                packet_loss_pct=0.0,
                sensors_configured=["pm2_5", "pm10", "co_ppm", "voc_index"],
                metadata_info={
                    "demo_location": True,
                    "physical_location_verified": False
                },
                source_mode="SIMULATION"
            ),
            Node(
                id="AKASHA-05",
                name="AKASHA Atmospheric Intelligence",
                node_type="WEATHER",
                tagline="Rain, Pressure, Wind & Severe Weather Intelligence",
                latitude=13.0827,
                longitude=80.2707,
                elevation_m=0.0,
                location_name="SIMULATION DEMO LOCATION - NOT FIELD DEPLOYED",
                status="SIMULATION",
                firmware_version="SOFTWARE-DOMAIN",
                hardware_rev="ESP32 WEATHER NODE - HARDWARE NOT CONNECTED",
                battery_pct=92.0,
                solar_voltage=0.0,
                signal_rssi=-83,
                packet_loss_pct=0.0,
                sensors_configured=[
                    "rain_intensity",
                    "pressure_hpa",
                    "wind_speed_kmh",
                    "wind_gust_kmh"
                ],
                metadata_info={
                    "demo_location": True,
                    "physical_location_verified": False
                },
                source_mode="SIMULATION"
            )
        ]

        for n in nodes:
            n.hardware_profile = DOMAIN_REGISTRY[n.id].hardware_profile.to_dict()
            existing = await db.execute(select(Node).where(Node.id == n.id))
            existing_node = existing.scalar_one_or_none()
            if not existing_node:
                db.add(n)
            elif existing_node.source_mode != "REAL":
                existing_node.location_name = n.location_name
                existing_node.latitude = n.latitude
                existing_node.longitude = n.longitude
                existing_node.elevation_m = 0.0
                existing_node.status = "SIMULATION"
                existing_node.firmware_version = n.firmware_version
                existing_node.hardware_rev = n.hardware_rev
                existing_node.solar_voltage = 0.0
                existing_node.source_mode = "SIMULATION"
                existing_node.metadata_info = n.metadata_info
                existing_node.hardware_profile = n.hardware_profile

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

