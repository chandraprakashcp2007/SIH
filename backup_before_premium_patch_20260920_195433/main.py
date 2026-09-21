"""
PRAHARI-NET Main Application Server Entrypoint
FastAPI REST + Real-time WebSockets
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.db.init_db import seed_data
from backend.app.websocket.manager import ws_manager
from backend.app.services.simulation_service import simulation_service

# Routers
from backend.app.api.auth import router as auth_router
from backend.app.api.nodes import router as nodes_router
from backend.app.api.telemetry import router as telemetry_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.predictions import router as predictions_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.network import router as network_router
from backend.app.api.simulator import router as simulator_router
from backend.app.api.copilot import router as copilot_router
from backend.app.api.reports import router as reports_router
from backend.app.api.settings import router as settings_router
from backend.app.api.logs import router as logs_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("prahari.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown procedures."""
    logger.info(f"Initializing {settings.PROJECT_NAME} v{settings.VERSION}...")
    # Ensure tables and seed data exist
    await seed_data()

    # Pre-warm Copilot knowledge index and resources
    from backend.app.copilot.service import copilot_service
    await copilot_service.prewarm()

    # Start simulation loop if enabled
    if settings.SIMULATION_MODE:
        logger.info("Auto-starting continuous disaster simulation loop...")
        await simulation_service.start()

    yield

    logger.info("Shutting down PRAHARI-NET background services...")
    await simulation_service.stop()
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Predictive Resilient Autonomous Hazard & Risk Intelligence Network (SIH26178)",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local Vite, PWA, and external field devices
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(nodes_router, prefix=settings.API_V1_STR)
app.include_router(telemetry_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(predictions_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(network_router, prefix=settings.API_V1_STR)
app.include_router(simulator_router, prefix=settings.API_V1_STR)
app.include_router(copilot_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)
app.include_router(logs_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root platform metadata."""
    return {
        "platform": "PRAHARI-NET",
        "tagline": "SENSE • PREDICT • ALERT • PROTECT",
        "status": "OPERATIONAL",
        "mode": "LOCAL_EDGE",
        "api_docs": f"{settings.API_V1_STR}/docs",
        "version": settings.VERSION
    }


@app.websocket("/ws/live")
async def websocket_live_stream(websocket: WebSocket):
    """
    Real-time bidirectional WebSocket stream for command centre telemetry,
    risk updates, sensor trust shifts, and audio alarm events.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Client can ping or send client commands
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=False)
