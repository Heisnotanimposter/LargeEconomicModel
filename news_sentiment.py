# news_sentiment.py
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from textblob import TextBlob
import streamlit as st

def scrape_bbc_business_news_rss():
    try:
        rss_url = "http://feeds.bbci.co.uk/news/business/rss.xml"
        response = requests.get(rss_url)
        root = ET.fromstring(response.content)
        headlines = [item.find('title').text for item in root.findall('.//item') if item.find('title') is not None]
        
        if not headlines:
            st.warning("No headlines found.")
            return pd.DataFrame()
        
        data = [{"Headline": hl, **TextBlob(hl).sentiment._asdict()} for hl in headlines]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return pd.DataFrame()

def calculate_fear_index(polarity, subjectivity):
    if polarity < -0.3 and subjectivity > 0.5:
        return 10  # High fear
    elif polarity < -0.2:
        return 7  # Moderate fear
    elif polarity < -0.1:
        return 4  # Low fear
    else:
        return 1  # No fear