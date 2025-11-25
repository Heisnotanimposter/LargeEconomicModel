"""
Economic indicators endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from datetime import date, datetime, timedelta
from api.models.schemas import (
    EconomicIndicatorResponse, IndicatorQuery, DataSource,
    ComparisonRequest, ComparisonResponse
)
from api.providers.manager import provider_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{indicator}", response_model=EconomicIndicatorResponse)
async def get_economic_indicator(
    indicator: str,
    country: str = Query(..., description="Country code (ISO 3166-1 alpha-3, e.g., USA, GBR, DEU)"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    source: DataSource = Query(DataSource.ALL, description="Preferred data source")
):
    """
    Get economic indicator data for a specific country
    
    ## Examples
    
    * `/api/v1/indicators/GDP?country=USA` - Get GDP data for United States
    * `/api/v1/indicators/UNEMPLOYMENT?country=GBR&start_date=2020-01-01` - Get UK unemployment since 2020
    * `/api/v1/indicators/INFLATION?country=DEU&source=world_bank` - Get German inflation from World Bank
    
    ## Common Indicators
    
    * **GDP** - Gross Domestic Product
    * **GDP_GROWTH** - GDP Growth Rate
    * **INFLATION** - Inflation Rate (CPI)
    * **UNEMPLOYMENT** - Unemployment Rate
    * **INTEREST_RATE** - Interest Rate / Central Bank Rate
    * **GOVERNMENT_DEBT** - Government Debt to GDP
    * **EXPORTS** - Exports of goods and services
    * **IMPORTS** - Imports of goods and services
    """
    
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=365 * 5)  # Last 5 years
        
        result = await provider_manager.get_indicator(
            indicator_id=indicator.upper(),
            country_code=country.upper(),
            start_date=start_date,
            end_date=end_date,
            preferred_source=source
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Indicator '{indicator}' not found for country '{country}'"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching indicator {indicator} for {country}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=Dict)
async def list_indicators():
    """
    List all available economic indicators from all data sources
    
    Returns a dictionary mapping data sources to their available indicators.
    """
    try:
        indicators = await provider_manager.list_available_indicators()
        return {
            "sources": provider_manager.get_available_sources(),
            "indicators": indicators,
            "total": sum(len(v) for v in indicators.values())
        }
    except Exception as e:
        logger.error(f"Error listing indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare", response_model=ComparisonResponse)
async def compare_indicators(request: ComparisonRequest):
    """
    Compare an economic indicator across multiple countries
    
    ## Example Request
    
    ```json
    {
        "indicator": "GDP_GROWTH",
        "countries": ["USA", "GBR", "DEU", "FRA", "JPN"],
        "start_date": "2020-01-01",
        "end_date": "2024-01-01",
        "source": "all"
    }
    ```
    
    This endpoint allows you to compare the same indicator across up to 10 countries.
    """
    try:
        countries_data = {}
        
        for country_code in request.countries:
            result = await provider_manager.get_indicator(
                indicator_id=request.indicator.upper(),
                country_code=country_code.upper(),
                start_date=request.start_date,
                end_date=request.end_date,
                preferred_source=request.source
            )
            if result:
                countries_data[country_code.upper()] = result
        
        if not countries_data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for indicator '{request.indicator}'"
            )
        
        return ComparisonResponse(
            indicator=request.indicator,
            indicator_name=list(countries_data.values())[0].name,
            countries=countries_data,
            comparison_period={
                "start": request.start_date or date.today() - timedelta(days=365 * 5),
                "end": request.end_date or date.today()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories/list", response_model=Dict)
async def list_indicator_categories():
    """
    List all available indicator categories
    
    Returns organized categories of economic indicators available in the API.
    """
    categories = {
        "macroeconomic": {
            "name": "Macroeconomic Indicators",
            "indicators": ["GDP", "GDP_GROWTH", "GDP_PER_CAPITA", "GNP"]
        },
        "prices": {
            "name": "Inflation & Prices",
            "indicators": ["INFLATION", "CPI", "PPI", "CORE_INFLATION"]
        },
        "labor": {
            "name": "Labor Market",
            "indicators": ["UNEMPLOYMENT", "EMPLOYMENT", "LABOR_FORCE", "WAGES"]
        },
        "monetary": {
            "name": "Monetary Policy",
            "indicators": ["INTEREST_RATE", "MONEY_SUPPLY", "M2", "CENTRAL_BANK_RATE"]
        },
        "fiscal": {
            "name": "Fiscal Policy",
            "indicators": ["GOVERNMENT_DEBT", "BUDGET_BALANCE", "GOVERNMENT_REVENUE"]
        },
        "trade": {
            "name": "International Trade",
            "indicators": ["EXPORTS", "IMPORTS", "CURRENT_ACCOUNT", "TRADE_BALANCE"]
        },
        "financial": {
            "name": "Financial Markets",
            "indicators": ["STOCK_INDEX", "BOND_YIELD", "EXCHANGE_RATE"]
        },
        "confidence": {
            "name": "Business & Consumer",
            "indicators": ["CONSUMER_CONFIDENCE", "BUSINESS_CONFIDENCE", "PMI"]
        }
    }
    
    return {
        "categories": categories,
        "total_categories": len(categories)
    }

