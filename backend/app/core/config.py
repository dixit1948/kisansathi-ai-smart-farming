"""
Application configuration via Pydantic Settings.
All secrets come from environment variables — never hardcoded.
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "CHANGE_ME_in_production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./kisansathi_dev.db"
    SQLITE_FALLBACK: bool = True

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_FALLBACK: bool = True

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION: str = "kisansathi_knowledge"

    # IBM watsonx.ai
    WATSONX_API_KEY: str = ""
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    GRANITE_TEXT_MODEL: str = "ibm/granite-4-h-small"
    GRANITE_VISION_MODEL: str = "ibm/granite-vision-3-2-2b"
    GRANITE_EMBED_MODEL: str = "ibm/granite-embedding-278m-multilingual"
    GRANITE_GUARDIAN_MODEL: str = "ibm/granite-guardian-3-8b"
    USE_MOCK_LLM: bool = True  # fallback if credentials not present

    # Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    OTP_EXPIRE_MINUTES: int = 10
    OTP_RATE_LIMIT_PER_HOUR: int = 5

    # Uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # WhatsApp
    WHATSAPP_VERIFY_TOKEN: str = "CHANGE_ME"
    WHATSAPP_APP_SECRET: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""

    # Weather
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"

    # Market
    AGMARKNET_API_KEY: str = ""

    # Observability
    LOG_LEVEL: str = "INFO"
    PROMETHEUS_ENABLED: bool = True

    # Scheduler
    DAILY_DIGEST_HOUR: int = 6
    WEATHER_SCAN_INTERVAL_HOURS: int = 1
    MARKET_REFRESH_INTERVAL_HOURS: int = 24

    @property
    def effective_database_url(self) -> str:
        if self.SQLITE_FALLBACK:
            return "sqlite+aiosqlite:///./kisansathi_dev.db"
        return self.DATABASE_URL

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.effective_database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
