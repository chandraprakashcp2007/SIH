from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import desc, select

from backend.app.core.database import AsyncSessionLocal
from backend.app.core.security import create_access_token
from backend.app.db.init_db import seed_data
from backend.app.domain.registry import DOMAIN_REGISTRY
from backend.app.main import app
from backend.app.models.telemetry import TelemetryRecord
from backend.app.models.nodes import Node
from backend.app.models.network import GatewayPacketLog
from backend.app.provenance import SourceMode
from backend.app.services.telemetry_service import telemetry_service


AUTH_HEADERS = {
    "Authorization": f"Bearer {create_access_token({'sub': 'admin', 'role': 'ADMIN', 'dev_auth_bypass': True})}"
}


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    import asyncio
    asyncio.run(seed_data())


def packet(node_id="JALA-01", sequence=800001, **overrides):
    payload = {
        "version": 1,
        "node_id": node_id,
        "sequence": sequence,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {"water_level_cm": 42.0, "rain_intensity": 1.0},
        "rssi": -70,
        "battery_pct": 90.0,
        "source_mode": "SIMULATION",
    }
    payload.update(overrides)
    return payload


def test_source_mode_has_all_canonical_values():
    assert {item.value for item in SourceMode} == {
        "REAL", "SIMULATION", "EXTERNAL_DATA", "REPLAY", "PLANNED"
    }


def test_registry_contains_five_truthful_domains():
    assert set(DOMAIN_REGISTRY) == {"JALA-01", "AGNI-02", "BHUMI-03", "VAYU-04", "AKASHA-05"}
    assert DOMAIN_REGISTRY["VAYU-04"].default_source_mode is SourceMode.SIMULATION
    assert DOMAIN_REGISTRY["VAYU-04"].risk_engine_available is True
    assert DOMAIN_REGISTRY["AKASHA-05"].default_source_mode is SourceMode.SIMULATION
    assert DOMAIN_REGISTRY["AKASHA-05"].risk_engine_available is True


@pytest.mark.asyncio
async def test_elements_api_returns_five_active_software_domains():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/elements",
            headers=AUTH_HEADERS
        )

    assert response.status_code == 200

    by_id = {
        item["domain_id"]: item
        for item in response.json()
    }

    assert len(by_id) == 5

    assert by_id["VAYU-04"]["source_mode"] == "SIMULATION"
    assert by_id["VAYU-04"]["risk_engine_state"] == "AVAILABLE"

    assert by_id["AKASHA-05"]["source_mode"] == "SIMULATION"
    assert by_id["AKASHA-05"]["risk_engine_state"] == "AVAILABLE"

    assert "NOT CONNECTED" in (
        by_id["VAYU-04"]["hardware_state"]
        .replace("_", " ")
    )


@pytest.mark.asyncio
async def test_legacy_simulation_flag_maps_to_simulation_and_stores_timestamps():
    telemetry_service.reset_sequence_tracking()
    device_time = datetime.now(timezone.utc) - timedelta(seconds=5)
    payload = packet(sequence=800002, timestamp=device_time.isoformat())
    payload.pop("source_mode")
    payload["is_simulation"] = True
    async with AsyncSessionLocal() as db:
        result = await telemetry_service.ingest_packet(db, payload, "TEST")
        stored = (await db.execute(
            select(TelemetryRecord)
            .where(TelemetryRecord.node_id == "JALA-01", TelemetryRecord.sequence == 800002)
            .order_by(desc(TelemetryRecord.server_received_at))
        )).scalars().first()
    assert result["source_mode"] == "SIMULATION"
    assert stored.source_mode == "SIMULATION"
    assert stored.device_timestamp is not None
    assert stored.server_received_at is not None
    assert stored.server_received_at >= stored.device_timestamp


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "node_id,metrics",
    [
        (
            "VAYU-04",
            {
                "pm2_5": 20.0,
                "pm10": 40.0,
                "co_ppm": 1.0,
                "voc_index": 90.0,
            },
        ),
        (
            "AKASHA-05",
            {
                "rain_intensity": 2.0,
                "pressure_hpa": 1008.0,
                "pressure_drop_hpa_3h": 0.3,
                "wind_speed_kmh": 12.0,
                "wind_gust_kmh": 18.0,
            },
        ),
    ],
)
async def test_vayu_akasha_software_pipeline_accepts_simulation(
    node_id,
    metrics,
):
    telemetry_service.reset_sequence_tracking()

    sequence = 810001 if node_id == "VAYU-04" else 820001

    payload = packet(
        node_id=node_id,
        sequence=sequence,
        metrics=metrics,
        source_mode="SIMULATION",
    )

    async with AsyncSessionLocal() as db:
        result = await telemetry_service.ingest_packet(
            db,
            payload,
            "SIMULATOR",
        )

    assert result["status"] == "success"
    assert result["source_mode"] == "SIMULATION"
    assert result["risk_band"] in {
        "NORMAL",
        "WATCH",
        "WARNING",
        "CRITICAL",
    }


@pytest.mark.asyncio
async def test_invalid_source_mode_is_rejected_safely():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/telemetry/ingest", json=packet(source_mode="MAGIC"), headers=AUTH_HEADERS
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_future_packet_is_quarantined():
    telemetry_service.reset_sequence_tracking()
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    async with AsyncSessionLocal() as db:
        result = await telemetry_service.ingest_packet(db, packet(sequence=800003, timestamp=future.isoformat()), "TEST")
    assert result["status"] == "quarantined"
    assert result["reason_code"] == "FUTURE_TIMESTAMP"


@pytest.mark.asyncio
async def test_stale_packet_is_quarantined():
    telemetry_service.reset_sequence_tracking()
    stale = datetime.now(timezone.utc) - timedelta(days=2)
    async with AsyncSessionLocal() as db:
        result = await telemetry_service.ingest_packet(db, packet(sequence=800004, timestamp=stale.isoformat()), "TEST")
    assert result["status"] == "quarantined"
    assert result["reason_code"] == "STALE_PACKET"


@pytest.mark.asyncio
async def test_simulation_cannot_replace_real_node_state():
    telemetry_service.reset_sequence_tracking()
    async with AsyncSessionLocal() as db:
        await telemetry_service.ingest_packet(db, packet(sequence=800010, source_mode="REAL"), "USB_SERIAL")
        node = await db.get(Node, "JALA-01")
        real_seen = node.last_seen
        result = await telemetry_service.ingest_packet(db, packet(sequence=800011, source_mode="SIMULATION"), "SIMULATOR")
        await db.refresh(node)
    assert result["source_mode"] == "SIMULATION"
    assert node.source_mode == "REAL"
    assert node.last_seen == real_seen


@pytest.mark.asyncio
async def test_replay_is_stored_without_overwriting_current_state():
    telemetry_service.reset_sequence_tracking()
    async with AsyncSessionLocal() as db:
        node = await db.get(Node, "JALA-01")
        before = (node.source_mode, node.last_seen)
        result = await telemetry_service.ingest_packet(db, packet(sequence=700000, source_mode="REPLAY"), "REPLAY")
        await db.refresh(node)
        stored = (await db.execute(select(TelemetryRecord).where(
            TelemetryRecord.node_id == "JALA-01", TelemetryRecord.sequence == 700000
        ))).scalar_one()
    assert result["status"] == "stored_isolated"
    assert stored.source_mode == "REPLAY"
    assert (node.source_mode, node.last_seen) == before


@pytest.mark.asyncio
async def test_external_data_is_not_stored_as_physical_telemetry():
    telemetry_service.reset_sequence_tracking()
    async with AsyncSessionLocal() as db:
        result = await telemetry_service.ingest_packet(db, packet(sequence=800020, source_mode="EXTERNAL_DATA"), "EXTERNAL")
        stored = (await db.execute(select(TelemetryRecord).where(
            TelemetryRecord.node_id == "JALA-01", TelemetryRecord.sequence == 800020
        ))).scalar_one_or_none()
    assert result["status"] == "quarantined"
    assert result["reason_code"] == "INVALID_SOURCE_MODE"
    assert stored is None


@pytest.mark.asyncio
async def test_sequence_gap_is_recorded():
    telemetry_service.reset_sequence_tracking()
    async with AsyncSessionLocal() as db:
        await telemetry_service.ingest_packet(db, packet(sequence=800030), "TEST")
        await telemetry_service.ingest_packet(db, packet(sequence=800033), "TEST")
        log = (await db.execute(select(GatewayPacketLog).where(
            GatewayPacketLog.node_id == "JALA-01", GatewayPacketLog.sequence == 800033
        ))).scalar_one()
    assert log.sequence_gap == 2
