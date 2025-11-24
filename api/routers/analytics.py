"""
Analytics endpoints for economic data analysis
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import date, datetime, timedelta
from api.models.schemas import AnalyticsRequest, AnalyticsResponse, DataSource
from api.providers.manager import provider_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/calculate", response_model=AnalyticsResponse)
async def calculate_analytics(request: AnalyticsRequest):
    """
    Perform analytics calculations on economic indicators
    
    ## Example Request
    
    ```json
    {
        "indicator": "GDP_GROWTH",
        "country": "USA",
        "start_date": "2020-01-01",
        "end_date": "2024-01-01",
        "calculations": ["mean", "median", "std", "min", "max", "trend"]
    }
    ```
    
    ## Available Calculations
    
    * **mean** - Average value
    * **median** - Median value
    * **std** - Standard deviation
    * **min** - Minimum value
    * **max** - Maximum value
    * **trend** - Linear trend analysis
    * **volatility** - Data volatility
    * **correlation** - Correlation with other indicators
    """
    try:
        # Fetch indicator data
        indicator_data = await provider_manager.get_indicator(
            indicator_id=request.indicator.upper(),
            country_code=request.country.upper(),
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        if not indicator_data or not indicator_data.data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {request.indicator} in {request.country}"
            )
        
        # Extract values
        values = [dp.value for dp in indicator_data.data]
        
        # Calculate statistics
        statistics = {}
        
        if "mean" in request.calculations:
            statistics["mean"] = sum(values) / len(values)
        
        if "median" in request.calculations:
            sorted_values = sorted(values)
            n = len(sorted_values)
            statistics["median"] = (
                sorted_values[n // 2] if n % 2 == 1
                else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
            )
        
        if "std" in request.calculations:
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            statistics["std"] = variance ** 0.5
        
        if "min" in request.calculations:
            statistics["min"] = min(values)
        
        if "max" in request.calculations:
            statistics["max"] = max(values)
        
        if "range" in request.calculations:
            statistics["range"] = max(values) - min(values)
        
        if "volatility" in request.calculations:
            if len(values) > 1:
                changes = [values[i] - values[i-1] for i in range(1, len(values))]
                mean_change = sum(changes) / len(changes)
                variance = sum((x - mean_change) ** 2 for x in changes) / len(changes)
                statistics["volatility"] = variance ** 0.5
        
        # Trend analysis
        trend_data = None
        if "trend" in request.calculations and len(values) > 2:
            # Simple linear regression
            n = len(values)
            x = list(range(n))
            y = values
            
            x_mean = sum(x) / n
            y_mean = sum(y) / n
            
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
                
                # Calculate R-squared
                y_pred = [slope * x[i] + intercept for i in range(n)]
                ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
                ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
                trend_data = {
                    "slope": slope,
                    "intercept": intercept,
                    "r_squared": r_squared,
                    "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
                }
        
        return AnalyticsResponse(
            indicator=request.indicator,
            country=request.country,
            period={
                "start": request.start_date,
                "end": request.end_date
            },
            statistics=statistics,
            trend=trend_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/correlation")
async def calculate_correlation(
    indicator1: str = Query(..., description="First indicator"),
    indicator2: str = Query(..., description="Second indicator"),
    country: str = Query(..., description="Country code"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
) -> Dict[str, Any]:
    """
    Calculate correlation between two economic indicators
    
    ## Examples
    
    * `/api/v1/analytics/correlation?indicator1=GDP_GROWTH&indicator2=UNEMPLOYMENT&country=USA`
    * `/api/v1/analytics/correlation?indicator1=INFLATION&indicator2=INTEREST_RATE&country=GBR&start_date=2020-01-01`
    
    Returns the Pearson correlation coefficient and interpretation.
    """
    try:
        # Set default dates
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=365 * 5)
        
        # Fetch both indicators
        data1 = await provider_manager.get_indicator(
            indicator1.upper(), country.upper(), start_date, end_date
        )
        data2 = await provider_manager.get_indicator(
            indicator2.upper(), country.upper(), start_date, end_date
        )
        
        if not data1 or not data2:
            raise HTTPException(
                status_code=404,
                detail="One or both indicators not found"
            )
        
        # Align data points by date
        dates1 = {dp.date: dp.value for dp in data1.data}
        dates2 = {dp.date: dp.value for dp in data2.data}
        
        common_dates = set(dates1.keys()) & set(dates2.keys())
        
        if len(common_dates) < 2:
            raise HTTPException(
                status_code=400,
                detail="Insufficient overlapping data points"
            )
        
        values1 = [dates1[d] for d in sorted(common_dates)]
        values2 = [dates2[d] for d in sorted(common_dates)]
        
        # Calculate Pearson correlation
        n = len(values1)
        mean1 = sum(values1) / n
        mean2 = sum(values2) / n
        
        numerator = sum((values1[i] - mean1) * (values2[i] - mean2) for i in range(n))
        denom1 = sum((values1[i] - mean1) ** 2 for i in range(n)) ** 0.5
        denom2 = sum((values2[i] - mean2) ** 2 for i in range(n)) ** 0.5
        
        correlation = numerator / (denom1 * denom2) if denom1 * denom2 != 0 else 0
        
        # Interpret correlation
        if abs(correlation) >= 0.7:
            strength = "strong"
        elif abs(correlation) >= 0.4:
            strength = "moderate"
        elif abs(correlation) >= 0.2:
            strength = "weak"
        else:
            strength = "very weak"
        
        direction = "positive" if correlation > 0 else "negative" if correlation < 0 else "none"
        
        return {
            "indicator1": {
                "id": indicator1,
                "name": data1.name
            },
            "indicator2": {
                "id": indicator2,
                "name": data2.name
            },
            "country": country.upper(),
            "period": {
                "start": start_date,
                "end": end_date
            },
            "correlation": round(correlation, 4),
            "interpretation": {
                "strength": strength,
                "direction": direction,
                "description": f"{strength.capitalize()} {direction} correlation"
            },
            "data_points": n
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating correlation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{country}")
async def get_economic_summary(
    country: str
) -> Dict[str, Any]:
    """
    Get a comprehensive economic summary for a country
    
    ## Examples
    
    * `/api/v1/analytics/summary/USA` - Get US economic summary
    * `/api/v1/analytics/summary/GBR` - Get UK economic summary
    
    Returns latest values for major economic indicators.
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        # Key indicators to fetch
        indicators = ["GDP", "INFLATION", "UNEMPLOYMENT", "INTEREST_RATE", "GOVERNMENT_DEBT"]
        
        summary = {
            "country": country.upper(),
            "as_of": datetime.now().isoformat(),
            "indicators": {}
        }
        
        for indicator in indicators:
            try:
                data = await provider_manager.get_indicator(
                    indicator, country.upper(), start_date, end_date
                )
                if data and data.data:
                    latest = data.data[-1]
                    summary["indicators"][indicator] = {
                        "name": data.name,
                        "value": latest.value,
                        "unit": latest.unit or data.unit,
                        "date": latest.date.isoformat(),
                        "source": data.source.value
                    }
            except Exception as e:
                logger.warning(f"Could not fetch {indicator} for {country}: {e}")
                continue
        
        if not summary["indicators"]:
            raise HTTPException(
                status_code=404,
                detail=f"No economic data found for {country}"
            )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting economic summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

