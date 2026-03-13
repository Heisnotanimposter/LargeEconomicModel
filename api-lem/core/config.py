"""LEM Engine configuration"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LEM Engine"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Large Economic Model - Industrial-grade economic data API"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "*",
    ]

    DATABASE_URL: str = "sqlite:///./lem_engine.db"
    DATABASE_ECHO: bool = False

    # L1: In-memory, 60s for hyper-volatile market data
    L1_TTL: int = 60
    # L2: Redis, 1hr for historical indicators (GDP, CPI, etc.)
    L2_TTL: int = 3600
    REDIS_URL: Optional[str] = None

    ENABLE_AUTH: bool = False
    API_KEY_NAME: str = "X-API-Key"
    API_KEYS: List[str] = []
    SECRET_KEY: str = "lem-secret-change-in-production"

    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Provider resilience
    PROVIDER_TIMEOUT: float = 10.0
    PROVIDER_MAX_RETRIES: int = 3
    CIRCUIT_BREAKER_THRESHOLD: int = 5

    FRED_API_KEY: Optional[str] = None
    ENABLE_FRED: bool = True
    ENABLE_WORLD_BANK: bool = True
    ENABLE_OECD: bool = True
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
