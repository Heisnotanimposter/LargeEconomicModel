"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class DataSource(str, Enum):
    """Available data sources"""
    FRED = "fred"
    WORLD_BANK = "world_bank"
    OECD = "oecd"
    IMF = "imf"
    TRADING_ECONOMICS = "trading_economics"
    ALL = "all"

class Frequency(str, Enum):
    """Data frequency options"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

class IndicatorCategory(str, Enum):
    """Economic indicator categories"""
    GDP = "gdp"
    INFLATION = "inflation"
    UNEMPLOYMENT = "unemployment"
    INTEREST_RATE = "interest_rate"
    GOVERNMENT_DEBT = "government_debt"
    TRADE = "trade"
    MONEY_SUPPLY = "money_supply"
    CONSUMER_CONFIDENCE = "consumer_confidence"
    BUSINESS_CONFIDENCE = "business_confidence"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    HOUSING = "housing"
    STOCK_MARKET = "stock_market"
    CURRENCY = "currency"

class DataPoint(BaseModel):
    """Single data point"""
    date: date
    value: float
    unit: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-01",
                "value": 2.5,
                "unit": "percent"
            }
        }

class EconomicIndicatorBase(BaseModel):
    """Base schema for economic indicator"""
    indicator_id: str = Field(..., description="Unique identifier for the indicator")
    name: str = Field(..., description="Human-readable name")
    category: IndicatorCategory
    description: Optional[str] = None
    unit: Optional[str] = Field(None, description="Unit of measurement (%, currency, index, etc.)")
    frequency: Frequency
    source: DataSource

class EconomicIndicatorResponse(EconomicIndicatorBase):
    """Economic indicator with data"""
    country_code: str = Field(..., description="ISO 3166-1 alpha-3 country code")
    country_name: str
    data: List[DataPoint]
    last_updated: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "indicator_id": "GDP",
                "name": "Gross Domestic Product",
                "category": "gdp",
                "description": "Total value of goods and services produced",
                "unit": "billion USD",
                "frequency": "quarterly",
                "source": "fred",
                "country_code": "USA",
                "country_name": "United States",
                "data": [
                    {"date": "2024-01-01", "value": 27500.0, "unit": "billion USD"}
                ],
                "last_updated": "2024-11-21T00:00:00",
                "metadata": {"seasonally_adjusted": True}
            }
        }

class CountryInfo(BaseModel):
    """Country information"""
    code: str = Field(..., description="ISO 3166-1 alpha-3 country code")
    name: str
    region: Optional[str] = None
    income_level: Optional[str] = None
    population: Optional[int] = None
    currency: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "USA",
                "name": "United States",
                "region": "North America",
                "income_level": "High income",
                "population": 331900000,
                "currency": "USD"
            }
        }

class IndicatorQuery(BaseModel):
    """Query parameters for indicator data"""
    indicator: str = Field(..., description="Indicator code (e.g., GDP, INFLATION)")
    country: str = Field(..., description="Country code (ISO 3166-1 alpha-3)")
    start_date: Optional[date] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date (YYYY-MM-DD)")
    source: DataSource = Field(DataSource.ALL, description="Preferred data source")
    frequency: Optional[Frequency] = Field(None, description="Data frequency")

class ComparisonRequest(BaseModel):
    """Request for comparing indicators across countries"""
    indicator: str
    countries: List[str] = Field(..., description="List of country codes")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    source: DataSource = DataSource.ALL
    
    @validator('countries')
    def validate_countries(cls, v):
        if len(v) < 2:
            raise ValueError('At least 2 countries required for comparison')
        if len(v) > 10:
            raise ValueError('Maximum 10 countries allowed for comparison')
        return v

class ComparisonResponse(BaseModel):
    """Response for country comparison"""
    indicator: str
    indicator_name: str
    countries: Dict[str, EconomicIndicatorResponse]
    comparison_period: Dict[str, date]
    
class AnalyticsRequest(BaseModel):
    """Request for analytics calculations"""
    indicator: str
    country: str
    start_date: date
    end_date: date
    calculations: List[str] = Field(
        default=["mean", "median", "std", "min", "max", "trend"],
        description="List of calculations to perform"
    )

class AnalyticsResponse(BaseModel):
    """Response for analytics"""
    indicator: str
    country: str
    period: Dict[str, date]
    statistics: Dict[str, float]
    trend: Optional[Dict[str, Any]] = None
    forecast: Optional[List[DataPoint]] = None

class MarketData(BaseModel):
    """Financial market data"""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "^GSPC",
                "name": "S&P 500",
                "price": 4500.50,
                "change": 25.30,
                "change_percent": 0.56,
                "volume": 3500000000,
                "market_cap": None,
                "timestamp": "2024-11-21T16:00:00"
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    status_code: int
    timestamp: float

