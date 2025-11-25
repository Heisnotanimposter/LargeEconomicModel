"""
Financial markets endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from api.models.schemas import MarketData
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/indices", response_model=List[MarketData])
async def get_market_indices(
    region: Optional[str] = Query(None, description="Filter by region")
):
    """
    Get major stock market indices
    
    ## Examples
    
    * `/api/v1/markets/indices` - Get all major indices
    * `/api/v1/markets/indices?region=US` - Get US indices
    * `/api/v1/markets/indices?region=Europe` - Get European indices
    
    ## Covered Indices
    
    * **S&P 500** - US large-cap stocks
    * **Dow Jones** - US industrial stocks
    * **NASDAQ** - US technology stocks
    * **FTSE 100** - UK stocks
    * **DAX** - German stocks
    * **Nikkei 225** - Japanese stocks
    * **Hang Seng** - Hong Kong stocks
    """
    
    # Sample data - in production, this would fetch real-time data
    sample_indices = [
        MarketData(
            symbol="^GSPC",
            name="S&P 500",
            price=4500.50,
            change=25.30,
            change_percent=0.56,
            volume=3500000000,
            timestamp=datetime.now()
        ),
        MarketData(
            symbol="^DJI",
            name="Dow Jones Industrial Average",
            price=35000.00,
            change=-50.00,
            change_percent=-0.14,
            volume=400000000,
            timestamp=datetime.now()
        ),
        MarketData(
            symbol="^IXIC",
            name="NASDAQ Composite",
            price=14000.00,
            change=100.00,
            change_percent=0.72,
            volume=5000000000,
            timestamp=datetime.now()
        )
    ]
    
    return sample_indices

@router.get("/currencies", response_model=List[dict])
async def get_currency_rates(
    base: str = Query("USD", description="Base currency code")
):
    """
    Get currency exchange rates
    
    ## Examples
    
    * `/api/v1/markets/currencies` - Get rates relative to USD
    * `/api/v1/markets/currencies?base=EUR` - Get rates relative to EUR
    
    ## Major Currencies
    
    * USD - US Dollar
    * EUR - Euro
    * GBP - British Pound
    * JPY - Japanese Yen
    * CHF - Swiss Franc
    * AUD - Australian Dollar
    * CAD - Canadian Dollar
    """
    
    # Sample data - in production, fetch from forex API
    sample_rates = {
        "USD": {
            "EUR": 0.85,
            "GBP": 0.73,
            "JPY": 110.50,
            "CHF": 0.92,
            "AUD": 1.35,
            "CAD": 1.25
        }
    }
    
    rates = sample_rates.get(base.upper(), sample_rates["USD"])
    
    return [
        {
            "base": base.upper(),
            "currency": currency,
            "rate": rate,
            "timestamp": datetime.now().isoformat()
        }
        for currency, rate in rates.items()
    ]

@router.get("/commodities", response_model=List[dict])
async def get_commodity_prices():
    """
    Get commodity prices
    
    ## Commodities
    
    * **Energy**: Crude Oil, Natural Gas
    * **Metals**: Gold, Silver, Copper
    * **Agriculture**: Wheat, Corn, Coffee
    """
    
    # Sample data
    commodities = [
        {
            "name": "Crude Oil (WTI)",
            "symbol": "CL",
            "price": 75.50,
            "unit": "USD/barrel",
            "change": 1.20,
            "change_percent": 1.61,
            "timestamp": datetime.now().isoformat()
        },
        {
            "name": "Gold",
            "symbol": "GC",
            "price": 1950.00,
            "unit": "USD/oz",
            "change": -5.00,
            "change_percent": -0.26,
            "timestamp": datetime.now().isoformat()
        },
        {
            "name": "Natural Gas",
            "symbol": "NG",
            "price": 2.80,
            "unit": "USD/MMBtu",
            "change": 0.05,
            "change_percent": 1.82,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    return commodities

