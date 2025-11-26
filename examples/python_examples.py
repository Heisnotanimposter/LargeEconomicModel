"""
Python examples for Economic Data API
"""
import requests
import json
from datetime import datetime, timedelta

# API Configuration
BASE_URL = "http://localhost:8000"
API_KEY = None  # Set this if authentication is enabled

# Headers (add API key if needed)
headers = {}
if API_KEY:
    headers["X-API-Key"] = API_KEY


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def example_1_get_gdp():
    """Example 1: Get GDP data for a country"""
    print_section("Example 1: Get GDP Data for USA")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/indicators/GDP",
        params={
            "country": "USA",
            "start_date": "2020-01-01"
        },
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Indicator: {data['name']}")
        print(f"Country: {data['country_name']}")
        print(f"Source: {data['source']}")
        print(f"\nLatest Data Point:")
        latest = data['data'][-1]
        print(f"  Date: {latest['date']}")
        print(f"  Value: {latest['value']} {latest.get('unit', '')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())


def example_2_compare_countries():
    """Example 2: Compare unemployment across countries"""
    print_section("Example 2: Compare Unemployment Rates")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/indicators/compare",
        json={
            "indicator": "UNEMPLOYMENT",
            "countries": ["USA", "GBR", "DEU", "FRA", "JPN"],
            "start_date": "2020-01-01"
        },
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Indicator: {data['indicator_name']}")
        print(f"\nLatest Unemployment Rates:")
        
        for country_code, country_data in data['countries'].items():
            if country_data['data']:
                latest = country_data['data'][-1]
                print(f"  {country_code}: {latest['value']:.2f}% ({latest['date']})")
    else:
        print(f"Error: {response.status_code}")


def example_3_calculate_statistics():
    """Example 3: Calculate statistics for an indicator"""
    print_section("Example 3: Calculate Inflation Statistics")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/analytics/calculate",
        json={
            "indicator": "INFLATION",
            "country": "USA",
            "start_date": "2020-01-01",
            "end_date": "2024-01-01",
            "calculations": ["mean", "median", "std", "min", "max", "trend"]
        },
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Indicator: {data['indicator']}")
        print(f"Country: {data['country']}")
        print(f"\nStatistics:")
        for key, value in data['statistics'].items():
            print(f"  {key.capitalize()}: {value:.2f}")
        
        if data.get('trend'):
            print(f"\nTrend Analysis:")
            trend = data['trend']
            print(f"  Direction: {trend['direction']}")
            print(f"  Slope: {trend['slope']:.4f}")
            print(f"  R-squared: {trend['r_squared']:.4f}")
    else:
        print(f"Error: {response.status_code}")


def example_4_correlation():
    """Example 4: Calculate correlation between indicators"""
    print_section("Example 4: GDP Growth vs Unemployment Correlation")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/analytics/correlation",
        params={
            "indicator1": "GDP_GROWTH",
            "indicator2": "UNEMPLOYMENT",
            "country": "USA",
            "start_date": "2015-01-01"
        },
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Indicator 1: {data['indicator1']['name']}")
        print(f"Indicator 2: {data['indicator2']['name']}")
        print(f"Country: {data['country']}")
        print(f"\nCorrelation: {data['correlation']:.4f}")
        print(f"Interpretation: {data['interpretation']['description']}")
        print(f"Data Points: {data['data_points']}")
    else:
        print(f"Error: {response.status_code}")


def example_5_economic_summary():
    """Example 5: Get economic summary for a country"""
    print_section("Example 5: Economic Summary for United Kingdom")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/analytics/summary/GBR",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Country: {data['country']}")
        print(f"As of: {data['as_of']}")
        print(f"\nKey Economic Indicators:")
        
        for indicator_id, indicator_data in data['indicators'].items():
            print(f"\n  {indicator_data['name']}:")
            print(f"    Value: {indicator_data['value']} {indicator_data.get('unit', '')}")
            print(f"    Date: {indicator_data['date']}")
            print(f"    Source: {indicator_data['source']}")
    else:
        print(f"Error: {response.status_code}")


def example_6_list_countries():
    """Example 6: List available countries"""
    print_section("Example 6: List Available Countries")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/countries/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total Unique Countries: {data['total_unique_countries']}")
        print(f"Total Entries: {data['total_entries']}")
        print(f"\nSources:")
        for source, countries in data['sources'].items():
            print(f"  {source}: {len(countries)} countries")
    else:
        print(f"Error: {response.status_code}")


def example_7_market_data():
    """Example 7: Get market indices"""
    print_section("Example 7: Market Indices")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/markets/indices",
        headers=headers
    )
    
    if response.status_code == 200:
        indices = response.json()
        print("Major Stock Market Indices:")
        for index in indices:
            print(f"\n  {index['name']} ({index['symbol']})")
            print(f"    Price: ${index['price']:,.2f}")
            print(f"    Change: ${index['change']:+,.2f} ({index['change_percent']:+.2f}%)")
    else:
        print(f"Error: {response.status_code}")


def example_8_data_sources():
    """Example 8: List data sources"""
    print_section("Example 8: Available Data Sources")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/sources",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print("Economic Data Sources:")
        for source in data['sources']:
            print(f"\n  {source['name']} - {source['full_name']}")
            print(f"    Provider: {source['provider']}")
            print(f"    Coverage: {source['coverage']}")
            print(f"    Indicators: {source['indicators']}")
            print(f"    Update Frequency: {source['update_frequency']}")
    else:
        print(f"Error: {response.status_code}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("  Economic Data API - Python Examples")
    print("  Make sure the API is running at http://localhost:8000")
    print("=" * 60)
    
    try:
        # Test API connection
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("\n❌ API is not responding. Please start the API server first.")
            return
        
        print("\n✅ API is running and healthy!")
        
        # Run examples
        examples = [
            example_1_get_gdp,
            example_2_compare_countries,
            example_3_calculate_statistics,
            example_4_correlation,
            example_5_economic_summary,
            example_6_list_countries,
            example_7_market_data,
            example_8_data_sources,
        ]
        
        for example in examples:
            try:
                example()
            except Exception as e:
                print(f"\n❌ Error running example: {e}")
        
        print("\n" + "=" * 60)
        print("  Examples completed!")
        print("=" * 60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API. Please ensure it's running at http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()

