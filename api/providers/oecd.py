"""
OECD Data provider
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

class OECDProvider(BaseDataProvider):
    """
    Provider for OECD Statistics
    API Documentation: https://data.oecd.org/api/
    """
    
    # Common indicator mappings
    INDICATOR_MAP = {
        "GDP": "GDP",
        "GDP_GROWTH": "QGDP",
        "INFLATION": "CPI",
        "UNEMPLOYMENT": "LUR",
        "INTEREST_RATE": "IRSTCI",
        "GOVERNMENT_DEBT": "GGDEBT",
        "CURRENT_ACCOUNT": "CAGDPPT",
    }
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://stats.oecd.org/sdmx-json/data"
        self.name = "OECD"
    
    async def get_indicator(
        self,
        indicator_id: str,
        country_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> Optional[EconomicIndicatorResponse]:
        """Fetch indicator data from OECD"""
        
        # Map indicator ID
        oecd_indicator = self.INDICATOR_MAP.get(indicator_id.upper(), indicator_id)
        
        # OECD uses different dataset codes
        # This is a simplified version
        logger.info(f"OECD provider: {oecd_indicator} for {country_code}")
        
        # Note: Full OECD implementation would require specific dataset codes
        # For now, return None to indicate this provider needs more configuration
        return None
    
    async def list_indicators(self) -> List[Dict[str, Any]]:
        """List available indicators"""
        return [
            {"id": k, "oecd_id": v, "name": k.replace("_", " ").title()}
            for k, v in self.INDICATOR_MAP.items()
        ]
    
    async def list_countries(self) -> List[Dict[str, Any]]:
        """List OECD member countries"""
        # OECD member countries
        members = [
            {"code": "AUS", "name": "Australia"},
            {"code": "AUT", "name": "Austria"},
            {"code": "BEL", "name": "Belgium"},
            {"code": "CAN", "name": "Canada"},
            {"code": "CHL", "name": "Chile"},
            {"code": "COL", "name": "Colombia"},
            {"code": "CZE", "name": "Czech Republic"},
            {"code": "DNK", "name": "Denmark"},
            {"code": "EST", "name": "Estonia"},
            {"code": "FIN", "name": "Finland"},
            {"code": "FRA", "name": "France"},
            {"code": "DEU", "name": "Germany"},
            {"code": "GRC", "name": "Greece"},
            {"code": "HUN", "name": "Hungary"},
            {"code": "ISL", "name": "Iceland"},
            {"code": "IRL", "name": "Ireland"},
            {"code": "ISR", "name": "Israel"},
            {"code": "ITA", "name": "Italy"},
            {"code": "JPN", "name": "Japan"},
            {"code": "KOR", "name": "South Korea"},
            {"code": "LVA", "name": "Latvia"},
            {"code": "LTU", "name": "Lithuania"},
            {"code": "LUX", "name": "Luxembourg"},
            {"code": "MEX", "name": "Mexico"},
            {"code": "NLD", "name": "Netherlands"},
            {"code": "NZL", "name": "New Zealand"},
            {"code": "NOR", "name": "Norway"},
            {"code": "POL", "name": "Poland"},
            {"code": "PRT", "name": "Portugal"},
            {"code": "SVK", "name": "Slovakia"},
            {"code": "SVN", "name": "Slovenia"},
            {"code": "ESP", "name": "Spain"},
            {"code": "SWE", "name": "Sweden"},
            {"code": "CHE", "name": "Switzerland"},
            {"code": "TUR", "name": "Turkey"},
            {"code": "GBR", "name": "United Kingdom"},
            {"code": "USA", "name": "United States"},
        ]
        return members
    
    def _map_category(self, indicator_id: str) -> IndicatorCategory:
        """Map indicator to category"""
        indicator = indicator_id.upper()
        if "GDP" in indicator:
            return IndicatorCategory.GDP
        elif "INFLATION" in indicator or "CPI" in indicator:
            return IndicatorCategory.INFLATION
        elif "UNEMPLOYMENT" in indicator:
            return IndicatorCategory.UNEMPLOYMENT
        elif "RATE" in indicator:
            return IndicatorCategory.INTEREST_RATE
        elif "DEBT" in indicator:
            return IndicatorCategory.GOVERNMENT_DEBT
        elif "ACCOUNT" in indicator:
            return IndicatorCategory.TRADE
        else:
            return IndicatorCategory.GDP

