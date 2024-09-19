# economic_data.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

def fetch_economic_data(indicator):
    urls = {
        "GDP": "https://tradingeconomics.com/country-list/gdp",
        "Inflation Rate": "https://tradingeconomics.com/country-list/inflation-rate",
        "Unemployment Rate": "https://tradingeconomics.com/country-list/unemployment-rate",
        "Interest Rate": "https://tradingeconomics.com/country-list/interest-rate",
        "Government Debt": "https://tradingeconomics.com/country-list/government-debt-to-gdp"
    }
    url = urls.get(indicator)
    table_class = "table table-hover table-heatmap"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': table_class})
        
        if table is None:
            st.error(f"Failed to retrieve data from {url}")
            return None
        
        headers = [header.get_text() for header in table.find_all('th')]
        rows = [[col.get_text().strip() for col in row.find_all('td')] for row in table.find_all('tr')[1:]]
        return pd.DataFrame(rows, columns=headers)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None