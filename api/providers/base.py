"""
Base class for data providers
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import aiohttp
import asyncio
from api.models.schemas import DataPoint, EconomicIndicatorResponse
from api.core.config import settings
import logging

logger = logging.getLogger(__name__)

class BaseDataProvider(ABC):
    """
    Abstract base class for economic data providers
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = ""
        self.name = "Base Provider"
        self.timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
    
    @abstractmethod
    async def get_indicator(
        self,
        indicator_id: str,
        country_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> Optional[EconomicIndicatorResponse]:
        """
        Fetch economic indicator data
        
        Args:
            indicator_id: Indicator identifier
            country_code: Country code (ISO 3166-1 alpha-3)
            start_date: Start date for data
            end_date: End date for data
            **kwargs: Additional provider-specific parameters
            
        Returns:
            EconomicIndicatorResponse or None if not found
        """
        pass
    
    @abstractmethod
    async def list_indicators(self) -> List[Dict[str, Any]]:
        """
        List available indicators
        
        Returns:
            List of indicator metadata
        """
        pass
    
    @abstractmethod
    async def list_countries(self) -> List[Dict[str, Any]]:
        """
        List available countries
        
        Returns:
            List of country metadata
        """
        pass
    
    async def fetch_with_retry(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data with retry logic
        
        Args:
            url: URL to fetch
            params: Query parameters
            headers: HTTP headers
            max_retries: Maximum number of retries
            
        Returns:
            JSON response or None
        """
        if max_retries is None:
            max_retries = settings.MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(url, params=params, headers=headers) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:
                            # Rate limited, wait and retry
                            wait_time = settings.RETRY_DELAY * (attempt + 1)
                            logger.warning(f"Rate limited by {self.name}, waiting {wait_time}s")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error(f"HTTP {response.status} from {self.name}: {url}")
                            return None
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching from {self.name}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(settings.RETRY_DELAY)
            except Exception as e:
                logger.error(f"Error fetching from {self.name}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(settings.RETRY_DELAY)
        
        return None
    
    def parse_date(self, date_str: str) -> Optional[date]:
        """
        Parse date string to date object
        
        Args:
            date_str: Date string
            
        Returns:
            date object or None
        """
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y%m%d",
            "%Y-%m",
            "%Y/%m",
            "%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None

