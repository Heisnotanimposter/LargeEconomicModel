"""
Economic Data API - Main Application
Provides comprehensive economic data from multiple sources including FRED, World Bank, OECD, and IMF
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import time
from contextlib import asynccontextmanager
import logging

from api.routers import economic_indicators, countries, markets, analytics
from api.core.config import settings
from api.core.database import init_db
from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.auth import AuthMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and cleanup on shutdown"""
    logger.info("Starting Economic Data API...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Economic Data API...")

# Create FastAPI application
app = FastAPI(
    title="Economic Data API",
    description="""
    ## Strong Economic Data API Provider
    
    This API provides comprehensive economic data from multiple authoritative sources:
    
    * **FRED (Federal Reserve Economic Data)** - US economic indicators
    * **World Bank** - Global development indicators
    * **OECD** - Economic data from developed nations
    * **IMF** - International financial statistics
    * **Trading Economics** - Real-time economic data
    
    ### Features
    
    * 📊 **Multiple Data Sources**: Access data from 5+ authoritative economic databases
    * 🌍 **Global Coverage**: 200+ countries and regions
    * 📈 **500+ Indicators**: GDP, inflation, unemployment, interest rates, and more
    * 🔄 **Real-time Updates**: Fresh data with intelligent caching
    * 📉 **Historical Data**: Access decades of historical economic data
    * 🔍 **Advanced Analytics**: Built-in calculations and trend analysis
    * 🚀 **High Performance**: Optimized with caching and async operations
    * 🔐 **Secure**: API key authentication and rate limiting
    
    ### Data Categories
    
    * **Macroeconomic Indicators**: GDP, GNP, National Income
    * **Inflation & Prices**: CPI, PPI, Core Inflation
    * **Labor Market**: Unemployment, Employment, Wages
    * **Monetary Policy**: Interest Rates, Money Supply, Central Bank Rates
    * **Fiscal Policy**: Government Debt, Budget Balance, Revenue
    * **Trade & Balance of Payments**: Exports, Imports, Current Account
    * **Financial Markets**: Stock Indices, Bond Yields, Exchange Rates
    * **Business & Consumer Confidence**: PMI, Consumer Sentiment
    """,
    version="1.0.0",
    contact={
        "name": "Economic Data API Support",
        "email": "support@economicdata.api",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
if settings.ENABLE_RATE_LIMITING:
    app.add_middleware(RateLimitMiddleware)

if settings.ENABLE_AUTH:
    app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(
    economic_indicators.router,
    prefix="/api/v1/indicators",
    tags=["Economic Indicators"]
)
app.include_router(
    countries.router,
    prefix="/api/v1/countries",
    tags=["Countries"]
)
app.include_router(
    markets.router,
    prefix="/api/v1/markets",
    tags=["Financial Markets"]
)
app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Economic Data API",
        "version": "1.0.0",
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "status": "operational",
        "features": {
            "data_sources": ["FRED", "World Bank", "OECD", "IMF", "Trading Economics"],
            "indicators": "500+",
            "countries": "200+",
            "real_time": True,
            "historical_data": True,
            "analytics": True
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@app.get("/api/v1/sources", tags=["Data Sources"])
async def get_data_sources():
    """Get information about available data sources"""
    return {
        "sources": [
            {
                "name": "FRED",
                "full_name": "Federal Reserve Economic Data",
                "provider": "Federal Reserve Bank of St. Louis",
                "coverage": "United States",
                "indicators": "500,000+",
                "update_frequency": "Daily",
                "website": "https://fred.stlouisfed.org/"
            },
            {
                "name": "World Bank",
                "full_name": "World Bank Open Data",
                "provider": "The World Bank",
                "coverage": "Global (217 countries)",
                "indicators": "1,400+",
                "update_frequency": "Quarterly/Annual",
                "website": "https://data.worldbank.org/"
            },
            {
                "name": "OECD",
                "full_name": "OECD Statistics",
                "provider": "Organisation for Economic Co-operation and Development",
                "coverage": "OECD Countries (38 members + partners)",
                "indicators": "1,000+",
                "update_frequency": "Monthly/Quarterly",
                "website": "https://data.oecd.org/"
            },
            {
                "name": "IMF",
                "full_name": "IMF Data",
                "provider": "International Monetary Fund",
                "coverage": "Global (190 countries)",
                "indicators": "500+",
                "update_frequency": "Monthly/Quarterly",
                "website": "https://www.imf.org/en/Data"
            },
            {
                "name": "Trading Economics",
                "full_name": "Trading Economics",
                "provider": "Trading Economics",
                "coverage": "Global (196 countries)",
                "indicators": "300+",
                "update_frequency": "Real-time",
                "website": "https://tradingeconomics.com/"
            }
        ]
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "status_code": 500,
            "timestamp": time.time()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

