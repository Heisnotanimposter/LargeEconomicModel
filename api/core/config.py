"""
Configuration management for Economic Data API
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Economic Data API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Strong Economic Data API Provider"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "*"
    ]
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./economic_data.db"
    DATABASE_ECHO: bool = False
    
    # Redis Configuration (for caching)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour default
    
    # Authentication
    ENABLE_AUTH: bool = False
    API_KEY_NAME: str = "X-API-Key"
    API_KEYS: List[str] = []  # Add your API keys here
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    
    # Rate Limiting
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # External API Keys
    FRED_API_KEY: Optional[str] = None
    WORLD_BANK_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    QUANDL_API_KEY: Optional[str] = None
    TRADING_ECONOMICS_API_KEY: Optional[str] = None
    
    # Data Provider Settings
    ENABLE_FRED: bool = True
    ENABLE_WORLD_BANK: bool = True
    ENABLE_OECD: bool = True
    ENABLE_IMF: bool = True
    ENABLE_TRADING_ECONOMICS: bool = True
    
    # Request Settings
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()

