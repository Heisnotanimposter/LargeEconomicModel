# Economic Data API & Analysis Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Overview

**A comprehensive Economic Data API and Analysis Platform** providing access to economic indicators from multiple authoritative sources including FRED, World Bank, OECD, and IMF. This platform offers real-time economic data, advanced analytics, and visualization tools for economists, data scientists, and developers.

### Streamlit Application
🔗 **Live Demo**: https://largeeconomicmodel-twxfx5skyfi4svtasud35f.streamlit.app/

## 🎯 Major Use Cases

### 1. Macroeconomic Trend Analysis
Analyze long-term trends in GDP, inflation, and unemployment to forecast economic cycles and make informed strategic decisions.

### 2. Cross-Country Comparison
Compare economic performance of multiple countries simultaneously to identify investment opportunities, benchmark performance, or evaluate policy effectiveness.

### 3. Real-time Market Monitoring
Track real-time economic indicators and market indices to make timely trading decisions and stay ahead of market movements.

### 4. Policy Impact Assessment
Evaluate the impact of monetary and fiscal policies (like interest rate changes or government spending) on key economic variables over time.

### 5. Automated Reporting
Generate automated, data-driven economic reports for stakeholders using the API's comprehensive and reliable data streams.

## 📊 Project Components

This repository contains two main components:

### 1. **Economic Data API** (Primary Focus)
A robust REST API providing economic data from multiple sources with advanced analytics capabilities.

**Key Features:**
- 📈 **500+ Economic Indicators** from 5+ authoritative sources
- 🌍 **200+ Countries** with comprehensive coverage
- 🔄 **Real-time Data** with intelligent caching
- 📉 **Historical Data** spanning decades
- 🔍 **Advanced Analytics** including trend analysis and correlations
- 🚀 **High Performance** with async operations
- 🔐 **Enterprise Security** with authentication and rate limiting

[**➡️ View Complete API Documentation**](API_README.md)

### 2. **Economic Analysis Tools**
Legacy Streamlit applications for economic data visualization and sentiment analysis.

**Components:**
- Economic data scraping from Trading Economics
- BBC Financial news sentiment analysis
- Interactive visualizations
- Machine learning models for sentiment prediction

## 🚀 Quick Start

### Option 1: Run the API (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/LargeEconomicModel.git
cd LargeEconomicModel

# Start the API (automated script)
./start_api.sh  # On Linux/Mac
# or
start_api.bat   # On Windows

# API will be available at:
# - Main: http://localhost:8000
# - Docs: http://localhost:8000/docs
```

### Option 2: Using Docker

```bash
# Clone and navigate
git clone https://github.com/yourusername/LargeEconomicModel.git
cd LargeEconomicModel

# Start with Docker Compose
docker-compose up -d

# Access the API
# - Main: http://localhost:8000
# - Docs: http://localhost:8000/docs
```

### Option 3: Run Streamlit Applications

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main Streamlit app
streamlit run Streamlit03.py
```

## 📚 Documentation

- **[API Documentation](API_README.md)** - Complete guide for the Economic Data API
- **[API Reference](http://localhost:8000/docs)** - Interactive API documentation (when running)
- **[Examples](examples/)** - Code examples in Python and other languages

## 🔌 API Usage Examples

### Python Example

```python
import requests

# Get GDP data for USA
response = requests.get(
    "http://localhost:8000/api/v1/indicators/GDP",
    params={"country": "USA", "start_date": "2020-01-01"}
)
data = response.json()
print(f"Latest GDP: {data['data'][-1]['value']}")
```

### Compare Multiple Countries

```python
response = requests.post(
    "http://localhost:8000/api/v1/indicators/compare",
    json={
        "indicator": "UNEMPLOYMENT",
        "countries": ["USA", "GBR", "DEU", "FRA"],
        "start_date": "2020-01-01"
    }
)
comparison = response.json()
```

### Calculate Analytics

```python
response = requests.post(
    "http://localhost:8000/api/v1/analytics/calculate",
    json={
        "indicator": "INFLATION",
        "country": "USA",
        "start_date": "2020-01-01",
        "end_date": "2024-01-01",
        "calculations": ["mean", "median", "std", "trend"]
    }
)
analytics = response.json()
```

[**➡️ More Examples**](examples/python_examples.py)

## 📊 Available Data Sources

| Source | Provider | Coverage | Indicators | Frequency |
|--------|----------|----------|------------|-----------|
| **FRED** | Federal Reserve | USA | 500,000+ | Daily |
| **World Bank** | World Bank | Global (217 countries) | 1,400+ | Quarterly/Annual |
| **OECD** | OECD | 38 members + partners | 1,000+ | Monthly/Quarterly |
| **IMF** | IMF | Global (190 countries) | 500+ | Monthly/Quarterly |
| **Trading Economics** | Trading Economics | Global (196 countries) | 300+ | Real-time |

## 🏗️ Project Structure

```
LargeEconomicModel/
├── api/                          # Economic Data API (Primary)
│   ├── main.py                   # FastAPI application
│   ├── core/                     # Core configurations
│   ├── models/                   # Data models
│   ├── providers/                # Data source providers
│   ├── routers/                  # API endpoints
│   └── middleware/               # Auth & rate limiting
├── examples/                     # Usage examples
│   └── python_examples.py
├── tests/                        # API tests
├── EconomicNewsCrawler/         # News crawler tools
├── News Sentiment Analysis/      # Sentiment analysis
├── OECDdatasets/                # OECD data tools
├── Experiment/                  # Experimental features
├── docker-compose.yml           # Docker configuration
├── api_requirements.txt         # API dependencies
├── requirements.txt             # Legacy app dependencies
├── start_api.sh                 # API startup script
└── API_README.md               # Detailed API docs
```

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- PostgreSQL (optional, SQLite by default)
- Redis (optional, for caching)

### Install API Dependencies
```bash
pip install -r api_requirements.txt
```

### Install Legacy App Dependencies
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Key configuration options:
- **FRED_API_KEY**: Get from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)
- **DATABASE_URL**: Database connection string
- **ENABLE_AUTH**: Enable API authentication
- **RATE_LIMIT_REQUESTS**: Rate limit per minute

See [API_README.md](API_README.md) for complete configuration guide.

## 🧪 Testing

```bash
# Run API tests
pytest

# Run with coverage
pytest --cov=api --cov-report=html

# Run specific test
pytest tests/test_api.py::test_health_check
```

## 🐳 Docker Deployment

```bash
# Development
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## 📈 API Endpoints

### Core Endpoints
- `GET /api/v1/indicators/{indicator}` - Get economic indicator data
- `POST /api/v1/indicators/compare` - Compare across countries
- `GET /api/v1/countries/` - List available countries
- `POST /api/v1/analytics/calculate` - Calculate statistics
- `GET /api/v1/analytics/correlation` - Correlation analysis
- `GET /api/v1/markets/indices` - Stock market indices

[**➡️ View All Endpoints**](API_README.md#-api-endpoints)

## 🔐 Security Features

- API key authentication
- Rate limiting (configurable)
- CORS support
- SQL injection prevention
- Input validation
- Secure headers

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

## 📧 Contact

For questions and support:
- Open an issue on GitHub
- Email: support@economicdata.api

## 🗺️ Roadmap

- [x] Core API with multiple data sources
- [x] Advanced analytics and correlations
- [x] Docker deployment
- [x] Comprehensive documentation
- [ ] WebSocket support for real-time updates
- [ ] Machine learning forecasting models
- [ ] Client SDKs (Python, JavaScript, R)
- [ ] GraphQL API
- [ ] Admin dashboard
- [ ] Data export (CSV, Excel, JSON)

---

**Built for economists, data scientists, and developers worldwide 🌍**
