
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str

    jwt_secret: str
    jwt_expire_minutes: int = 60

    ml_service_url: str = "http://localhost:8001"
    ml_timeout_seconds: int = 5
    ml_use_stub: bool = True

    upload_dir: str = "backend/uploads"
    max_image_mb: int = 5
    cors_origins: str = "http://localhost:5173"   #CORS_ORIGINS=https://your-frontend.onrender.com

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
