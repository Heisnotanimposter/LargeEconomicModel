"""
LEM Engine - Large Economic Model API
Industrial-grade throughput with ORJSON, uvloop, L1/L2 caching, and resilience.
"""
# Force uvloop for maximum I/O performance (Unix only)
import sys
if sys.platform != "win32":
    try:
        import uvloop
        uvloop.install()
    except ImportError:
        pass  # Fallback to default asyncio event loop

from contextlib import asynccontextmanager
import time
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.requests import Request as StarletteRequest

from api_lem.core.config import settings
from api_lem.core.database import init_db
from api_lem.core.cache import init_cache, close_cache

from api.routers import economic_indicators, countries, markets, analytics
from api_lem.middleware.rate_limit import RateLimitMiddleware
from api_lem.middleware.auth import AuthMiddleware

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize LEM Engine resources"""
    logger.info("Starting LEM Engine...")
    await init_db()
    await init_cache()
    logger.info("L1/L2 cache initialized")
    yield
    await close_cache()
    logger.info("LEM Engine shutdown complete")


# Override default JSON response with ORJSON for massive payload throughput
app = FastAPI(
    title="LEM Engine",
    description="Large Economic Model - Industrial-grade economic data API",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.ENABLE_RATE_LIMITING:
    app.add_middleware(RateLimitMiddleware)
if settings.ENABLE_AUTH:
    app.add_middleware(AuthMiddleware)

app.include_router(economic_indicators.router, prefix="/api/v1/indicators", tags=["Indicators"])
app.include_router(countries.router, prefix="/api/v1/countries", tags=["Countries"])
app.include_router(markets.router, prefix="/api/v1/markets", tags=["Markets"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "LEM Engine",
        "brand": "Large Economic Model",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "timestamp": time.time(), "version": "1.0.0"}


@app.get("/api/v1/sources", tags=["Data Sources"])
async def get_data_sources():
    return {
        "sources": [
            {"name": "FRED", "full_name": "Federal Reserve Economic Data"},
            {"name": "World Bank", "full_name": "World Bank Open Data"},
            {"name": "OECD", "full_name": "OECD Statistics"},
            {"name": "IMF", "full_name": "IMF Data"},
        ]
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: StarletteRequest, exc: HTTPException):
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code, "timestamp": time.time()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: StarletteRequest, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return ORJSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500, "timestamp": time.time()},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_lem.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
