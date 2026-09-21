"""
PRAHARI-NET Core Configuration Module
Smart India Hackathon 2026 - Problem Statement SIH26178
"""
from typing import List, Union, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    PROJECT_NAME: str = "PRAHARI-NET"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_flag(cls, v: Any) -> bool:
        if isinstance(v, str):
            clean = v.strip().lower()
            if clean in ("true", "1", "yes", "on", "debug"):
                return True
            return False
        return bool(v)

    # Host & Port
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    FRONTEND_PORT: int = 5173

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/prahari.db"

    # Security
    SECRET_KEY: str = "prahari-net-sih2026-super-secure-local-secret-key-change-in-prod-32bytes"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"
    DEV_AUTH_BYPASS: bool = False

    # Hardware Serial & LoRa
    SERIAL_PORT: str = "COM3"
    SERIAL_BAUD_RATE: int = 115200
    GATEWAY_MODE: str = "SIMULATOR"  # Options: REAL, SIMULATOR
    GATEWAY_POLL_INTERVAL_SEC: float = 2.0

    # Simulation & Demo
    SIMULATION_MODE: bool = True
    SIMULATION_TICK_RATE_MS: int = 2000

    # Vision Integration
    VISION_ENABLED: bool = False
    VISION_STREAM_URL: str = ""
    VISION_MODEL_PATH: str = ""

    # Copilot & LLM Configuration
    COPILOT_ENABLED: bool = True
    COPILOT_MODE: str = "auto"  # auto, online, offline
    COPILOT_FAST_PATH: bool = True
    COPILOT_STREAMING: bool = True
    COPILOT_CACHE_ENABLED: bool = True
    COPILOT_TOOL_TIMEOUT_MS: int = 2000
    COPILOT_MAX_CONTEXT_CHUNKS: int = 6
    COPILOT_MAX_HISTORY_MESSAGES: int = 12

    LLM_PROVIDER: str = "LOCAL_DETERMINISTIC"  # LOCAL_DETERMINISTIC, OPENAI, GEMINI, OLLAMA
    LLM_MODEL: str = "local-expert-v1"
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    LLM_TIMEOUT_SECONDS: int = 20
    RAG_ENABLED: bool = True

    # Map & Network
    MAP_PROVIDER: str = "OPENSTREETMAP"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
    ]


settings = Settings()
