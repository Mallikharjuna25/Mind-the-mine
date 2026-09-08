import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI MineGuard - Module 2 Field Operation & Inspection Management"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mineguard_module2.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "mineguard-super-secret-jwt-key-sih26024")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "backend/storage/uploads")
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
