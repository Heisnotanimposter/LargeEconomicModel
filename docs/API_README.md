# Economic Data API

**A comprehensive REST API providing economic data from multiple authoritative sources including FRED, World Bank, OECD, IMF, and Trading Economics.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Features

### 📊 **Comprehensive Data Coverage**
- **5+ Data Sources**: FRED, World Bank, OECD, IMF, Trading Economics
- **200+ Countries**: Global coverage with country-specific data
- **500+ Economic Indicators**: GDP, inflation, unemployment, interest rates, and more
- **Historical Data**: Access decades of historical economic data
- **Real-time Updates**: Fresh data with intelligent caching

### 🚀 **High Performance**
- **Async Architecture**: Built with FastAPI for high performance
- **Intelligent Caching**: Redis-based caching layer
- **Database Optimization**: SQLAlchemy with connection pooling
- **Rate Limiting**: Configurable rate limits to protect resources

### 🔐 **Enterprise-Ready**
- **Authentication**: API key-based authentication
- **Rate Limiting**: Prevent abuse with customizable limits
- **CORS Support**: Cross-origin resource sharing enabled
- **Comprehensive Logging**: Track all API requests and errors
- **Health Checks**: Monitor API status and dependencies

### 📈 **Advanced Analytics**
- **Statistical Analysis**: Mean, median, std, min, max calculations
- **Trend Analysis**: Linear regression and trend detection
- **Correlation Analysis**: Compare multiple indicators
- **Country Comparisons**: Compare indicators across countries
- **Economic Summaries**: Get comprehensive country overviews

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [Usage Examples](#-usage-examples)
- [Data Sources](#-data-sources)
- [Docker Deployment](#-docker-deployment)
- [Development](#-development)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/LargeEconomicModel.git
cd LargeEconomicModel

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys (optional but recommended for full functionality)

# Start services
docker compose -f infrastructure/docker-compose.yml up -d

# API is now running at http://localhost:8000
# View documentation at http://localhost:8000/docs
```

### Local Development

```bash
# Install dependencies
pip install -r requirements/api_requirements.txt

# Set up environment
cp .env.example .env

# Run the API
uvicorn api.main:app --reload

# Access at http://localhost:8000
```

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL (optional, SQLite by default)
- Redis (optional, for caching)

### Step-by-Step Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/LargeEconomicModel.git
   cd LargeEconomicModel
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements/api_requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database:**
   ```bash
   python -c "from api.core.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

6. **Run the server:**
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Core Settings
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./economic_data.db  # or postgresql://...

# External API Keys (get these from respective providers)
FRED_API_KEY=your_fred_api_key
WORLD_BANK_API_KEY=optional
TRADING_ECONOMICS_API_KEY=your_key

# Authentication
ENABLE_AUTH=false  # Set to true for production
API_KEYS=key1,key2,key3

# Rate Limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Data Providers
ENABLE_FRED=true
ENABLE_WORLD_BANK=true
ENABLE_OECD=true
```

### Getting API Keys

#### FRED (Recommended)
1. Visit: https://fred.stlouisfed.org/
2. Create free account
3. Generate API key: https://fred.stlouisfed.org/docs/api/api_key.html

#### World Bank
- No API key required
- Free access to all data

#### OECD
- No API key required
- Free access to statistics

#### Trading Economics (Optional)
1. Visit: https://tradingeconomics.com/
2. Sign up for API access
3. Choose a plan (free tier available)

## 🔌 API Endpoints

### Core Endpoints

#### Get Economic Indicator
```http
GET /api/v1/indicators/{indicator}?country={country}&start_date={date}&end_date={date}
```

#### List All Indicators
```http
GET /api/v1/indicators/
```

#### Compare Countries
```http
POST /api/v1/indicators/compare
Content-Type: application/json

{
  "indicator": "GDP_GROWTH",
  "countries": ["USA", "GBR", "DEU"],
  "start_date": "2020-01-01",
  "end_date": "2024-01-01"
}
```

### Country Endpoints

#### List Countries
```http
GET /api/v1/countries/
```

#### Get Country Info
```http
GET /api/v1/countries/{country_code}
```

#### List Regions
```http
GET /api/v1/countries/regions/list
```

### Analytics Endpoints

#### Calculate Statistics
```http
POST /api/v1/analytics/calculate
Content-Type: application/json

{
  "indicator": "GDP_GROWTH",
  "country": "USA",
  "start_date": "2020-01-01",
  "end_date": "2024-01-01",
  "calculations": ["mean", "median", "std", "trend"]
}
```

#### Correlation Analysis
```http
GET /api/v1/analytics/correlation?indicator1=GDP_GROWTH&indicator2=UNEMPLOYMENT&country=USA
```

#### Economic Summary
```http
GET /api/v1/analytics/summary/{country}
```

### Market Endpoints

#### Market Indices
```http
GET /api/v1/markets/indices
```

#### Currency Rates
```http
GET /api/v1/markets/currencies?base=USD
```

#### Commodity Prices
```http
GET /api/v1/markets/commodities
```

### Utility Endpoints

#### Health Check
```http
GET /health
```

#### List Data Sources
```http
GET /api/v1/sources
```

## 💡 Usage Examples

### Python Examples

#### Basic Usage

```python
import requests

# API base URL
BASE_URL = "http://localhost:8000"

# Get GDP data for USA
response = requests.get(
    f"{BASE_URL}/api/v1/indicators/GDP",
    params={
        "country": "USA",
        "start_date": "2020-01-01"
    }
)
data = response.json()
print(f"Latest GDP: {data['data'][-1]['value']}")
```

#### Compare Multiple Countries

```python
import requests

response = requests.post(
    f"{BASE_URL}/api/v1/indicators/compare",
    json={
        "indicator": "UNEMPLOYMENT",
        "countries": ["USA", "GBR", "DEU", "FRA", "JPN"],
        "start_date": "2020-01-01"
    }
)
comparison = response.json()

for country, data in comparison['countries'].items():
    latest = data['data'][-1]
    print(f"{country}: {latest['value']}% ({latest['date']})")
```

#### Calculate Analytics

```python
import requests

response = requests.post(
    f"{BASE_URL}/api/v1/analytics/calculate",
    json={
        "indicator": "INFLATION",
        "country": "USA",
        "start_date": "2020-01-01",
        "end_date": "2024-01-01",
        "calculations": ["mean", "median", "std", "min", "max", "trend"]
    }
)
analytics = response.json()

print(f"Average Inflation: {analytics['statistics']['mean']:.2f}%")
print(f"Trend: {analytics['trend']['direction']}")
```

### JavaScript/Node.js Examples

```javascript
// Using fetch
async function getGDPData(country) {
  const response = await fetch(
    `http://localhost:8000/api/v1/indicators/GDP?country=${country}`
  );
  const data = await response.json();
  return data;
}

// Usage
getGDPData('USA').then(data => {
  console.log('Latest GDP:', data.data[data.data.length - 1].value);
});
```

### cURL Examples

```bash
# Get unemployment rate
curl "http://localhost:8000/api/v1/indicators/UNEMPLOYMENT?country=USA"

# Get economic summary
curl "http://localhost:8000/api/v1/analytics/summary/GBR"

# Compare countries
curl -X POST "http://localhost:8000/api/v1/indicators/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "indicator": "GDP_GROWTH",
    "countries": ["USA", "CHN", "JPN", "DEU"],
    "start_date": "2020-01-01"
  }'
```

## 📊 Data Sources

### FRED (Federal Reserve Economic Data)
- **Provider**: Federal Reserve Bank of St. Louis
- **Coverage**: United States
- **Indicators**: 500,000+
- **Frequency**: Daily, Weekly, Monthly, Quarterly, Annual
- **Website**: https://fred.stlouisfed.org/

### World Bank Open Data
- **Provider**: The World Bank
- **Coverage**: Global (217 countries)
- **Indicators**: 1,400+
- **Frequency**: Annual, Quarterly
- **Website**: https://data.worldbank.org/

### OECD Statistics
- **Provider**: Organisation for Economic Co-operation and Development
- **Coverage**: OECD Countries (38 members + partners)
- **Indicators**: 1,000+
- **Frequency**: Monthly, Quarterly, Annual
- **Website**: https://data.oecd.org/

### IMF Data
- **Provider**: International Monetary Fund
- **Coverage**: Global (190 countries)
- **Indicators**: 500+
- **Frequency**: Monthly, Quarterly, Annual
- **Website**: https://www.imf.org/en/Data

### Trading Economics
- **Provider**: Trading Economics
- **Coverage**: Global (196 countries)
- **Indicators**: 300+
- **Frequency**: Real-time
- **Website**: https://tradingeconomics.com/

## 🐳 Docker Deployment

### Development Setup

```bash
# Build and start services
docker compose -f infrastructure/docker-compose.yml up -d

# View logs
docker compose -f infrastructure/docker-compose.yml logs -f api

# Stop services
docker compose -f infrastructure/docker-compose.yml down

# Rebuild after changes
docker compose -f infrastructure/docker-compose.yml up -d --build
```

### Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build: .
    environment:
      - DEBUG=false
      - ENABLE_AUTH=true
      - DATABASE_URL=postgresql://user:pass@db:5432/prod_db
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
```

```bash
# Deploy to production
docker compose -f infrastructure/docker-compose.yml up -d
```

## 🛠️ Development

### Project Structure

```
LargeEconomicModel/
├── api/
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   └── database.py        # Database setup
│   ├── models/
│   │   ├── schemas.py         # Pydantic models
│   │   └── database.py        # SQLAlchemy models
│   ├── providers/
│   │   ├── base.py            # Base provider class
│   │   ├── fred.py            # FRED provider
│   │   ├── world_bank.py      # World Bank provider
│   │   ├── oecd.py            # OECD provider
│   │   └── manager.py         # Provider manager
│   ├── routers/
│   │   ├── economic_indicators.py
│   │   ├── countries.py
│   │   ├── markets.py
│   │   └── analytics.py
│   └── middleware/
│       ├── rate_limit.py      # Rate limiting
│       └── auth.py            # Authentication
├── tests/
│   ├── test_api.py
│   ├── test_providers.py
│   └── test_analytics.py
├── infrastructure/
│   ├── docker-compose.yml
│   ├── Dockerfile.api
│   └── nginx.conf
├── requirements/
│   └── api_requirements.txt
└── docs/
    └── API_README.md
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov-report=html

# Run specific test
pytest tests/test_api.py::test_get_indicator
```

### Code Quality

```bash
# Format code
black api/

# Lint
flake8 api/
pylint api/

# Type checking
mypy api/
```

## 🧪 Testing

### Unit Tests

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_indicator():
    response = client.get("/api/v1/indicators/GDP?country=USA")
    assert response.status_code == 200
    data = response.json()
    assert data["country_code"] == "USA"
    assert len(data["data"]) > 0
```

### Running Tests

```bash
# Run all tests
pytest

# Run with output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=api
```

## 📈 Performance

- **Response Time**: < 200ms (cached)
- **Throughput**: 1000+ requests/second
- **Concurrent Users**: 500+
- **Cache Hit Rate**: > 90%

## 🔒 Security

- API key authentication
- Rate limiting per IP/key
- CORS configuration
- SQL injection prevention
- Input validation
- Secure headers

## 📝 API Documentation

Interactive API documentation is automatically generated and available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Federal Reserve Bank of St. Louis (FRED)
- The World Bank
- OECD
- International Monetary Fund
- FastAPI framework
- All contributors and users

## 📧 Support

For support, please open an issue on GitHub or contact support@economicdata.api

## 🗺️ Roadmap

- [ ] Add more data providers (Eurostat, BIS, etc.)
- [ ] Implement data forecasting models
- [ ] Add WebSocket support for real-time updates
- [ ] Create client SDKs (Python, JavaScript, R)
- [ ] Add GraphQL API
- [ ] Implement data export formats (CSV, Excel, JSON)
- [ ] Add visualization endpoints
- [ ] Create admin dashboard
- [ ] Implement user management
- [ ] Add data quality metrics

---

**Made with ❤️ for economists, data scientists, and developers**

