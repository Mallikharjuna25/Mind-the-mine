"""
Core Application Configuration
Provides strongly-typed settings using pydantic-settings, loading from .env if present.
Maintains clear migration path between SQLite (local MVP) and PostgreSQL/PostGIS.
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application Meta
    PROJECT_NAME: str = "AI MineGuard — Smart Governance & Compliance System"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    # SQLite async default for local MVP, effortlessly swappable to PostgreSQL
    # e.g., postgresql+asyncpg://user:pass@localhost:5432/ai_mineguard
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_mineguard.db"
    SYNC_DATABASE_URL: str = "sqlite:///./ai_mineguard.db"

    # Security & JWT
    SECRET_KEY: str = "ai_mineguard_secret_key_sih26024_super_secure_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    # Module 1 AI & Vision Engine Thresholds
    CCTV_CONFIDENCE_THRESHOLD: float = 0.75
    CCTV_DEDUPLICATION_WINDOW_SECONDS: int = 30
    OCR_CONFIDENCE_THRESHOLD: float = 0.70

    # Risk Engine Weights (Formula: R = w_v * V + w_e * E + w_p * P + w_s * S)
    RISK_WEIGHT_VIOLATIONS: float = 0.40
    RISK_WEIGHT_ENVIRONMENT: float = 0.25
    RISK_WEIGHT_PRODUCTION: float = 0.15
    RISK_WEIGHT_EQUIPMENT_SAFETY: float = 0.20

    # SLA Escalation Thresholds (in minutes)
    SLA_LEVEL_1_MINUTES: int = 15   # Immediate: Safety Officer
    SLA_LEVEL_2_MINUTES: int = 60   # Medium: Mine Manager
    SLA_LEVEL_3_MINUTES: int = 240  # Critical: Director Technical / Corporate

    # Assets & Upload Directories
    UPLOAD_DIR: str = "storage/uploads"
    SYNTHETIC_ASSETS_DIR: str = "storage/synthetic_assets"


settings = Settings()
