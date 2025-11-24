"""
Data provider manager - coordinates multiple data sources
"""
from typing import List, Optional, Dict, Any
from datetime import date
from api.providers.fred import FREDProvider
from api.providers.world_bank import WorldBankProvider
from api.providers.oecd import OECDProvider
from api.models.schemas import (
    EconomicIndicatorResponse, DataSource
)
from api.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ProviderManager:
    """
    Manages multiple data providers and coordinates data fetching
    """
    
    def __init__(self):
        self.providers = {}
        
        # Initialize providers based on settings
        if settings.ENABLE_FRED:
            self.providers[DataSource.FRED] = FREDProvider()
        
        if settings.ENABLE_WORLD_BANK:
            self.providers[DataSource.WORLD_BANK] = WorldBankProvider()
        
        if settings.ENABLE_OECD:
            self.providers[DataSource.OECD] = OECDProvider()
    
    async def get_indicator(
        self,
        indicator_id: str,
        country_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        preferred_source: DataSource = DataSource.ALL
    ) -> Optional[EconomicIndicatorResponse]:
        """
        Fetch indicator data, trying multiple sources if needed
        
        Args:
            indicator_id: Indicator identifier
            country_code: Country code (ISO 3166-1 alpha-3)
            start_date: Start date
            end_date: End date
            preferred_source: Preferred data source
            
        Returns:
            EconomicIndicatorResponse or None
        """
        
        # If specific source requested, try only that
        if preferred_source != DataSource.ALL and preferred_source in self.providers:
            try:
                result = await self.providers[preferred_source].get_indicator(
                    indicator_id, country_code, start_date, end_date
                )
                if result:
                    return result
            except Exception as e:
                logger.error(f"Error from {preferred_source}: {e}")
        
        # Try all providers in order of preference
        source_order = self._get_source_order(country_code)
        
        for source in source_order:
            if source not in self.providers:
                continue
            
            try:
                result = await self.providers[source].get_indicator(
                    indicator_id, country_code, start_date, end_date
                )
                if result:
                    logger.info(f"Successfully fetched {indicator_id} for {country_code} from {source}")
                    return result
            except Exception as e:
                logger.error(f"Error fetching from {source}: {e}")
                continue
        
        logger.warning(f"Could not fetch {indicator_id} for {country_code} from any source")
        return None
    
    def _get_source_order(self, country_code: str) -> List[DataSource]:
        """
        Determine optimal source order based on country
        
        Args:
            country_code: Country code
            
        Returns:
            Ordered list of data sources to try
        """
        # US data: prefer FRED
        if country_code == "USA":
            return [DataSource.FRED, DataSource.WORLD_BANK, DataSource.OECD]
        
        # OECD countries: prefer OECD
        oecd_countries = [
            "AUS", "AUT", "BEL", "CAN", "CHL", "COL", "CZE", "DNK", "EST", "FIN",
            "FRA", "DEU", "GRC", "HUN", "ISL", "IRL", "ISR", "ITA", "JPN", "KOR",
            "LVA", "LTU", "LUX", "MEX", "NLD", "NZL", "NOR", "POL", "PRT", "SVK",
            "SVN", "ESP", "SWE", "CHE", "TUR", "GBR"
        ]
        if country_code in oecd_countries:
            return [DataSource.OECD, DataSource.WORLD_BANK, DataSource.FRED]
        
        # All others: prefer World Bank
        return [DataSource.WORLD_BANK, DataSource.OECD, DataSource.FRED]
    
    async def list_available_indicators(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List indicators from all available providers
        
        Returns:
            Dictionary mapping source to indicator list
        """
        all_indicators = {}
        
        for source, provider in self.providers.items():
            try:
                indicators = await provider.list_indicators()
                all_indicators[source.value] = indicators
            except Exception as e:
                logger.error(f"Error listing indicators from {source}: {e}")
        
        return all_indicators
    
    async def list_available_countries(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List countries from all available providers
        
        Returns:
            Dictionary mapping source to country list
        """
        all_countries = {}
        
        for source, provider in self.providers.items():
            try:
                countries = await provider.list_countries()
                all_countries[source.value] = countries
            except Exception as e:
                logger.error(f"Error listing countries from {source}: {e}")
        
        return all_countries
    
    def get_available_sources(self) -> List[str]:
        """Get list of enabled data sources"""
        return [source.value for source in self.providers.keys()]

# Global provider manager instance
provider_manager = ProviderManager()

