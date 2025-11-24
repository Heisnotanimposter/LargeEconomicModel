"""
World Bank Data provider
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from api.providers.base import BaseDataProvider
from api.models.schemas import (
    DataPoint, EconomicIndicatorResponse, DataSource,
    Frequency, IndicatorCategory
)
import logging

logger = logging.getLogger(__name__)

class WorldBankProvider(BaseDataProvider):
    """
    Provider for World Bank Open Data
    API Documentation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
    """
    
    # Common indicator mappings
    INDICATOR_MAP = {
        "GDP": "NY.GDP.MKTP.CD",
        "GDP_GROWTH": "NY.GDP.MKTP.KD.ZG",
        "GDP_PER_CAPITA": "NY.GDP.PCAP.CD",
        "INFLATION": "FP.CPI.TOTL.ZG",
        "UNEMPLOYMENT": "SL.UEM.TOTL.ZS",
        "POPULATION": "SP.POP.TOTL",
        "GOVERNMENT_DEBT": "GC.DOD.TOTL.GD.ZS",
        "EXPORTS": "NE.EXP.GNFS.ZS",
        "IMPORTS": "NE.IMP.GNFS.ZS",
        "FDI": "BX.KLT.DINV.WD.GD.ZS",
        "CURRENT_ACCOUNT": "BN.CAB.XOKA.GD.ZS",
    }
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.worldbank.org/v2"
        self.name = "World Bank"
    
    async def get_indicator(
        self,
        indicator_id: str,
        country_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> Optional[EconomicIndicatorResponse]:
        """Fetch indicator data from World Bank"""
        
        # Map indicator ID
        wb_indicator = self.INDICATOR_MAP.get(indicator_id.upper(), indicator_id)
        
        # Build URL
        url = f"{self.base_url}/country/{country_code}/indicator/{wb_indicator}"
        
        params = {
            "format": "json",
            "per_page": 1000
        }
        
        if start_date:
            params["date"] = f"{start_date.year}:{end_date.year if end_date else datetime.now().year}"
        
        # Fetch data
        result = await self.fetch_with_retry(url, params)
        if not result or len(result) < 2:
            return None
        
        metadata = result[0]
        data = result[1]
        
        if not data:
            return None
        
        # Parse data points
        data_points = []
        for item in data:
            if item.get('value') is not None:
                try:
                    data_points.append(DataPoint(
                        date=date(int(item['date']), 1, 1),
                        value=float(item['value']),
                        unit=None
                    ))
                except (ValueError, TypeError):
                    continue
        
        # Sort by date
        data_points.sort(key=lambda x: x.date)
        
        # Get indicator metadata
        indicator_info = await self._get_indicator_info(wb_indicator)
        
        return EconomicIndicatorResponse(
            indicator_id=wb_indicator,
            name=indicator_info.get('name', indicator_id) if indicator_info else indicator_id,
            category=self._map_category(indicator_id),
            description=indicator_info.get('sourceNote') if indicator_info else None,
            unit=indicator_info.get('unit') if indicator_info else None,
            frequency=Frequency.ANNUAL,
            source=DataSource.WORLD_BANK,
            country_code=country_code.upper(),
            country_name=data[0].get('country', {}).get('value', country_code) if data else country_code,
            data=data_points,
            last_updated=datetime.now(),
            metadata={
                "indicator_id": wb_indicator,
                "source_organization": indicator_info.get('sourceOrganization') if indicator_info else None
            }
        )
    
    async def _get_indicator_info(self, indicator_id: str) -> Optional[Dict[str, Any]]:
        """Get indicator metadata"""
        url = f"{self.base_url}/indicator/{indicator_id}"
        params = {"format": "json"}
        
        result = await self.fetch_with_retry(url, params)
        if result and len(result) > 1 and result[1]:
            return result[1][0]
        return None
    
    async def list_indicators(self) -> List[Dict[str, Any]]:
        """List available indicators"""
        return [
            {"id": k, "wb_id": v, "name": k.replace("_", " ").title()}
            for k, v in self.INDICATOR_MAP.items()
        ]
    
    async def list_countries(self) -> List[Dict[str, Any]]:
        """List available countries"""
        url = f"{self.base_url}/country"
        params = {"format": "json", "per_page": 300}
        
        result = await self.fetch_with_retry(url, params)
        if not result or len(result) < 2:
            return []
        
        countries = []
        for country in result[1]:
            if country.get('region', {}).get('value') != 'Aggregates':
                countries.append({
                    "code": country['id'],
                    "name": country['name'],
                    "region": country.get('region', {}).get('value'),
                    "income_level": country.get('incomeLevel', {}).get('value'),
                })
        
        return countries
    
    def _map_category(self, indicator_id: str) -> IndicatorCategory:
        """Map indicator to category"""
        indicator = indicator_id.upper()
        if "GDP" in indicator:
            return IndicatorCategory.GDP
        elif "INFLATION" in indicator or "CPI" in indicator:
            return IndicatorCategory.INFLATION
        elif "UNEMPLOYMENT" in indicator:
            return IndicatorCategory.UNEMPLOYMENT
        elif "DEBT" in indicator:
            return IndicatorCategory.GOVERNMENT_DEBT
        elif "EXPORT" in indicator or "IMPORT" in indicator or "TRADE" in indicator:
            return IndicatorCategory.TRADE
        else:
            return IndicatorCategory.GDP

