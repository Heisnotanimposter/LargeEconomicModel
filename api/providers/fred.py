"""
FRED (Federal Reserve Economic Data) provider
"""
from typing import List, Optional, Dict, Any
from datetime import date
from api.providers.base import BaseDataProvider
from api.models.schemas import (
    DataPoint, EconomicIndicatorResponse, DataSource,
    Frequency, IndicatorCategory
)
from api.core.config import settings
import logging

logger = logging.getLogger(__name__)

class FREDProvider(BaseDataProvider):
    """
    Provider for FRED (Federal Reserve Economic Data)
    API Documentation: https://fred.stlouisfed.org/docs/api/
    """
    
    # Mapping of common indicators to FRED series IDs
    INDICATOR_MAP = {
        "GDP": "GDP",
        "GDPC1": "GDPC1",  # Real GDP
        "INFLATION": "CPIAUCSL",  # CPI
        "UNEMPLOYMENT": "UNRATE",
        "INTEREST_RATE": "FEDFUNDS",
        "GOVERNMENT_DEBT": "GFDEGDQ188S",
        "CONSUMER_CONFIDENCE": "UMCSENT",
        "INDUSTRIAL_PRODUCTION": "INDPRO",
        "RETAIL_SALES": "RSXFS",
        "HOUSING_STARTS": "HOUST",
        "M2": "M2SL",  # Money Supply
    }
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.FRED_API_KEY)
        self.base_url = "https://api.stlouisfed.org/fred"
        self.name = "FRED"
    
    async def get_indicator(
        self,
        indicator_id: str,
        country_code: str = "USA",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> Optional[EconomicIndicatorResponse]:
        """
        Fetch indicator data from FRED
        Note: FRED primarily contains US data
        """
        # FRED is US-centric
        if country_code != "USA":
            logger.info(f"FRED provider only supports USA data, got: {country_code}")
            return None
        
        if not self.api_key:
            logger.warning("FRED API key not configured")
            return None
        
        # Map indicator to FRED series ID
        series_id = self.INDICATOR_MAP.get(indicator_id.upper(), indicator_id)
        
        # Fetch series info
        series_info = await self._get_series_info(series_id)
        if not series_info:
            return None
        
        # Fetch observations
        observations = await self._get_observations(
            series_id, start_date, end_date
        )
        if not observations:
            return None
        
        # Parse data points
        data_points = []
        for obs in observations:
            if obs.get('value') and obs['value'] != '.':
                try:
                    data_points.append(DataPoint(
                        date=self.parse_date(obs['date']),
                        value=float(obs['value']),
                        unit=series_info.get('units')
                    ))
                except (ValueError, TypeError):
                    continue
        
        return EconomicIndicatorResponse(
            indicator_id=series_id,
            name=series_info.get('title', indicator_id),
            category=self._map_category(indicator_id),
            description=series_info.get('notes'),
            unit=series_info.get('units'),
            frequency=self._map_frequency(series_info.get('frequency')),
            source=DataSource.FRED,
            country_code="USA",
            country_name="United States",
            data=data_points,
            last_updated=series_info.get('last_updated'),
            metadata={
                "series_id": series_id,
                "seasonal_adjustment": series_info.get('seasonal_adjustment'),
                "frequency_short": series_info.get('frequency_short')
            }
        )
    
    async def _get_series_info(self, series_id: str) -> Optional[Dict[str, Any]]:
        """Get series metadata"""
        url = f"{self.base_url}/series"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        
        result = await self.fetch_with_retry(url, params)
        if result and 'seriess' in result and result['seriess']:
            return result['seriess'][0]
        return None
    
    async def _get_observations(
        self,
        series_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Get series observations"""
        url = f"{self.base_url}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        
        if start_date:
            params["observation_start"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["observation_end"] = end_date.strftime("%Y-%m-%d")
        
        result = await self.fetch_with_retry(url, params)
        if result and 'observations' in result:
            return result['observations']
        return None
    
    async def list_indicators(self) -> List[Dict[str, Any]]:
        """List available indicators"""
        return [
            {"id": k, "series_id": v, "name": k.replace("_", " ").title()}
            for k, v in self.INDICATOR_MAP.items()
        ]
    
    async def list_countries(self) -> List[Dict[str, Any]]:
        """List available countries (FRED is US only)"""
        return [{"code": "USA", "name": "United States"}]
    
    def _map_frequency(self, freq: Optional[str]) -> Frequency:
        """Map FRED frequency to our enum"""
        mapping = {
            "Daily": Frequency.DAILY,
            "Weekly": Frequency.WEEKLY,
            "Monthly": Frequency.MONTHLY,
            "Quarterly": Frequency.QUARTERLY,
            "Annual": Frequency.ANNUAL,
        }
        return mapping.get(freq, Frequency.MONTHLY)
    
    def _map_category(self, indicator_id: str) -> IndicatorCategory:
        """Map indicator to category"""
        indicator = indicator_id.upper()
        if "GDP" in indicator:
            return IndicatorCategory.GDP
        elif "INFLATION" in indicator or "CPI" in indicator:
            return IndicatorCategory.INFLATION
        elif "UNEMPLOYMENT" in indicator or "UNRATE" in indicator:
            return IndicatorCategory.UNEMPLOYMENT
        elif "RATE" in indicator or "FEDFUNDS" in indicator:
            return IndicatorCategory.INTEREST_RATE
        elif "DEBT" in indicator:
            return IndicatorCategory.GOVERNMENT_DEBT
        elif "CONFIDENCE" in indicator:
            return IndicatorCategory.CONSUMER_CONFIDENCE
        elif "M2" in indicator:
            return IndicatorCategory.MONEY_SUPPLY
        elif "INDUSTRIAL" in indicator:
            return IndicatorCategory.MANUFACTURING
        elif "RETAIL" in indicator:
            return IndicatorCategory.RETAIL
        elif "HOUSING" in indicator or "HOUST" in indicator:
            return IndicatorCategory.HOUSING
        else:
            return IndicatorCategory.GDP

