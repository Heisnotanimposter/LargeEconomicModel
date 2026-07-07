import requests
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st

def fetch_economic_data(url, table_class):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': table_class})
        
        if table is None:
            st.error(f"Failed to retrieve data from {url}")
            return None

        headers = [header.get_text() for header in table.find_all('th')]
        rows = []
        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')
            row_data = [column.get_text().strip() for column in columns]
            rows.append(row_data)
        
        df = pd.DataFrame(rows, columns=headers)
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from {url}: {e}")
        return None

def scrape_bbc_business_news_rss():
    try:
        rss_url = "http://feeds.bbci.co.uk/news/business/rss.xml"
        response = requests.get(rss_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        headlines = []
        for item in root.findall('.//item'):
            title = item.find('title').text
            if title:
                headlines.append(title)

        if not headlines:
            st.warning("No headlines found.")
            return pd.DataFrame()

        data = []
        from textblob import TextBlob
        for headline in headlines:
            sentiment = TextBlob(headline).sentiment
            data.append([headline, sentiment.polarity, sentiment.subjectivity])

        df = pd.DataFrame(data, columns=['Headline', 'Polarity', 'Subjectivity'])
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching BBC news: {e}")
        return pd.DataFrame()
    except ET.ParseError as e:
        st.error(f"Error parsing BBC news feed: {e}")
        return pd.DataFrame()
