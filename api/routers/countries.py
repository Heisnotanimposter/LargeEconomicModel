"""
Countries endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from api.models.schemas import CountryInfo
from api.providers.manager import provider_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=Dict)
async def list_countries(
    region: Optional[str] = Query(None, description="Filter by region"),
    source: Optional[str] = Query(None, description="Filter by data source")
):
    """
    List all available countries from all data sources
    
    ## Query Parameters
    
    * **region**: Filter by region (e.g., "North America", "Europe", "Asia")
    * **source**: Filter by data source (e.g., "fred", "world_bank", "oecd")
    
    ## Examples
    
    * `/api/v1/countries/` - List all countries
    * `/api/v1/countries/?region=Europe` - List European countries
    * `/api/v1/countries/?source=oecd` - List OECD countries
    """
    try:
        all_countries = await provider_manager.list_available_countries()
        
        # Filter by source if specified
        if source:
            all_countries = {k: v for k, v in all_countries.items() if k == source}
        
        # Filter by region if specified
        if region:
            for source_name, countries in all_countries.items():
                all_countries[source_name] = [
                    c for c in countries
                    if c.get('region', '').lower() == region.lower()
                ]
        
        # Count total unique countries
        unique_countries = set()
        for countries in all_countries.values():
            unique_countries.update(c['code'] for c in countries)
        
        return {
            "sources": all_countries,
            "total_unique_countries": len(unique_countries),
            "total_entries": sum(len(v) for v in all_countries.values())
        }
        
    except Exception as e:
        logger.error(f"Error listing countries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{country_code}", response_model=CountryInfo)
async def get_country_info(
    country_code: str
):
    """
    Get detailed information about a specific country
    
    ## Examples
    
    * `/api/v1/countries/USA` - Get info about United States
    * `/api/v1/countries/GBR` - Get info about United Kingdom
    * `/api/v1/countries/DEU` - Get info about Germany
    """
    try:
        all_countries = await provider_manager.list_available_countries()
        
        # Search for country in all sources
        country_info = None
        for source, countries in all_countries.items():
            for country in countries:
                if country['code'].upper() == country_code.upper():
                    country_info = CountryInfo(**country)
                    break
            if country_info:
                break
        
        if not country_info:
            raise HTTPException(
                status_code=404,
                detail=f"Country '{country_code}' not found"
            )
        
        return country_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting country info for {country_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regions/list", response_model=Dict)
async def list_regions():
    """
    List all available regions
    
    Returns a list of world regions covered by the API.
    """
    regions = {
        "regions": [
            {
                "name": "North America",
                "countries": ["USA", "CAN", "MEX"]
            },
            {
                "name": "Europe",
                "countries": ["GBR", "DEU", "FRA", "ITA", "ESP", "NLD", "BEL", "SWE", "NOR", "DNK"]
            },
            {
                "name": "Asia",
                "countries": ["CHN", "JPN", "KOR", "IND", "IDN", "THA", "SGP", "MYS"]
            },
            {
                "name": "Oceania",
                "countries": ["AUS", "NZL"]
            },
            {
                "name": "South America",
                "countries": ["BRA", "ARG", "CHL", "COL", "PER"]
            },
            {
                "name": "Africa",
                "countries": ["ZAF", "NGA", "EGY", "KEN", "GHA"]
            },
            {
                "name": "Middle East",
                "countries": ["SAU", "ARE", "ISR", "TUR", "IRN"]
            }
        ],
        "total": 7
    }
    
    return regions

