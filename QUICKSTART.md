# Quick Start Guide - Economic Data API

Get up and running with the Economic Data API in 5 minutes!

## 🚀 Fastest Way to Start

### Option 1: Automated Startup Script (Easiest)

#### Linux/Mac:
```bash
./start_api.sh
```

#### Windows:
```bash
start_api.bat
```

**That's it!** The script will:
- Create a virtual environment
- Install all dependencies
- Set up the database
- Start the API server

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Option 2: Docker (Best for Production)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Option 3: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r api_requirements.txt

# Start the API
uvicorn api.main:app --reload
```

## 🔑 Getting API Keys (Optional but Recommended)

To access all data sources, you'll need API keys:

### 1. FRED (Federal Reserve Economic Data) - FREE
1. Visit: https://fred.stlouisfed.org/
2. Create a free account
3. Go to: https://fred.stlouisfed.org/docs/api/api_key.html
4. Copy your API key
5. Add to `.env`: `FRED_API_KEY=your_key_here`

### 2. World Bank - NO KEY NEEDED ✅
World Bank data is freely accessible without an API key.

### 3. OECD - NO KEY NEEDED ✅
OECD data is freely accessible without an API key.

### 4. Trading Economics (Optional) - PAID
1. Visit: https://tradingeconomics.com/
2. Sign up for API access
3. Add to `.env`: `TRADING_ECONOMICS_API_KEY=your_key_here`

## 📝 Configuration

Create a `.env` file in the project root:

```bash
# Minimal configuration
DEBUG=true
FRED_API_KEY=your_fred_api_key_here

# Optional: Enable authentication
ENABLE_AUTH=false

# Optional: Configure rate limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
```

## ✅ Verify Installation

### 1. Check API Health
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": 1700000000.0,
  "version": "1.0.0"
}
```

### 2. Test an Endpoint
```bash
curl "http://localhost:8000/api/v1/indicators/GDP?country=USA"
```

### 3. View Interactive Documentation
Open your browser to: http://localhost:8000/docs

You can test all endpoints directly from this interface!

## 🎯 First API Calls

### Example 1: Get GDP Data
```bash
curl "http://localhost:8000/api/v1/indicators/GDP?country=USA&start_date=2020-01-01"
```

### Example 2: List Available Countries
```bash
curl "http://localhost:8000/api/v1/countries/"
```

### Example 3: Get Economic Summary
```bash
curl "http://localhost:8000/api/v1/analytics/summary/USA"
```

### Example 4: Compare Countries
```bash
curl -X POST "http://localhost:8000/api/v1/indicators/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "indicator": "UNEMPLOYMENT",
    "countries": ["USA", "GBR", "DEU"],
    "start_date": "2020-01-01"
  }'
```

## 🐍 Python Quick Start

```python
import requests

# Base URL
API_URL = "http://localhost:8000"

# Get GDP data
response = requests.get(
    f"{API_URL}/api/v1/indicators/GDP",
    params={"country": "USA", "start_date": "2020-01-01"}
)
data = response.json()

# Print latest value
latest = data['data'][-1]
print(f"Latest GDP: {latest['value']} {latest['unit']}")
```

## 🔧 Common Issues & Solutions

### Issue: Port 8000 already in use
**Solution**: Change the port
```bash
uvicorn api.main:app --port 8001
```

### Issue: Module not found errors
**Solution**: Install dependencies
```bash
pip install -r api_requirements.txt
```

### Issue: Database errors
**Solution**: Initialize the database
```bash
python -c "from api.core.database import init_db, engine, Base; Base.metadata.create_all(bind=engine)"
```

### Issue: FRED API returns no data
**Solution**: Check your API key in `.env`:
```bash
FRED_API_KEY=your_actual_key_here
```

## 📚 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read Full Documentation**: See [API_README.md](API_README.md)
3. **Try Examples**: Run `python examples/python_examples.py`
4. **Check Data Sources**: Visit http://localhost:8000/api/v1/sources

## 💡 Tips

- **Use the interactive docs** at `/docs` to test endpoints
- **Start without API keys** - World Bank and OECD work without them
- **Enable caching** with Redis for better performance
- **Use Docker** for production deployments
- **Check logs** if something doesn't work

## 🆘 Need Help?

- **Documentation**: [API_README.md](API_README.md)
- **Examples**: [examples/python_examples.py](examples/python_examples.py)
- **Issues**: Open an issue on GitHub
- **API Status**: Check http://localhost:8000/health

## 🎉 You're Ready!

Your Economic Data API is now running! Start making requests and building amazing applications with economic data.

**Happy coding! 🚀**

