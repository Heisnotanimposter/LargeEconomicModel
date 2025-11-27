"""
Unit tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "version" in data
        assert "features" in data


class TestDataSources:
    """Test data source endpoints"""
    
    def test_list_data_sources(self):
        """Test listing data sources"""
        response = client.get("/api/v1/sources")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert len(data["sources"]) > 0
        
        # Check FRED is in sources
        fred = next((s for s in data["sources"] if s["name"] == "FRED"), None)
        assert fred is not None
        assert fred["full_name"] == "Federal Reserve Economic Data"


class TestIndicatorEndpoints:
    """Test economic indicator endpoints"""
    
    def test_list_indicators(self):
        """Test listing available indicators"""
        response = client.get("/api/v1/indicators/")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert "indicators" in data
        assert "total" in data
    
    def test_list_indicator_categories(self):
        """Test listing indicator categories"""
        response = client.get("/api/v1/indicators/categories/list")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "total_categories" in data
        assert len(data["categories"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_indicator_invalid_country(self):
        """Test getting indicator with invalid country"""
        response = client.get("/api/v1/indicators/GDP?country=INVALID")
        # Should return 404 or 500 depending on implementation
        assert response.status_code in [404, 500]


class TestCountryEndpoints:
    """Test country endpoints"""
    
    def test_list_countries(self):
        """Test listing countries"""
        response = client.get("/api/v1/countries/")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert "total_unique_countries" in data
    
    def test_list_regions(self):
        """Test listing regions"""
        response = client.get("/api/v1/countries/regions/list")
        assert response.status_code == 200
        data = response.json()
        assert "regions" in data
        assert len(data["regions"]) > 0


class TestMarketEndpoints:
    """Test market data endpoints"""
    
    def test_get_market_indices(self):
        """Test getting market indices"""
        response = client.get("/api/v1/markets/indices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "symbol" in data[0]
            assert "name" in data[0]
            assert "price" in data[0]
    
    def test_get_currency_rates(self):
        """Test getting currency rates"""
        response = client.get("/api/v1/markets/currencies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_commodity_prices(self):
        """Test getting commodity prices"""
        response = client.get("/api/v1/markets/commodities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAnalyticsEndpoints:
    """Test analytics endpoints"""
    
    @pytest.mark.asyncio
    async def test_calculate_analytics_missing_data(self):
        """Test analytics with missing data"""
        response = client.post(
            "/api/v1/analytics/calculate",
            json={
                "indicator": "INVALID",
                "country": "USA",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "calculations": ["mean", "median"]
            }
        )
        # Should return 404 for invalid indicator
        assert response.status_code in [404, 500]
    
    @pytest.mark.asyncio
    async def test_correlation_invalid_indicators(self):
        """Test correlation with invalid indicators"""
        response = client.get(
            "/api/v1/analytics/correlation",
            params={
                "indicator1": "INVALID1",
                "indicator2": "INVALID2",
                "country": "USA"
            }
        )
        assert response.status_code in [404, 500]


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_headers(self):
        """Test that rate limit headers are present"""
        response = client.get("/health")
        assert response.status_code == 200
        # Check for rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_not_found(self):
        """Test 404 error"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_query_params(self):
        """Test invalid query parameters"""
        response = client.get("/api/v1/indicators/GDP")  # Missing required country param
        # Should return 422 (validation error)
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

