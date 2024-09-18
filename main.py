import streamlit as st
import pandas as pd
from data_fetcher import fetch_economic_data, scrape_bbc_business_news_rss
from visualizer import visualize_polarity_distribution, visualize_rag_status_distribution, visualize_fear_index_distribution
from ml_models import run_ml_models
from utils import display_icon, calculate_fear_index

# Page Configuration
st.set_page_config(page_title="Economic News & Sentiment Analysis", layout="wide")

# Title and description
st.title("🌐 Economic Data & Sentiment Analysis")
st.markdown("Analyze the economic indicators and sentiment analysis from BBC News with AI-powered models.")

# Sidebar for selecting economic indicators
urls = {
    "GDP": "https://tradingeconomics.com/country-list/gdp",
    "Inflation Rate": "https://tradingeconomics.com/country-list/inflation-rate",
    "Unemployment Rate": "https://tradingeconomics.com/country-list/unemployment-rate",
    "Interest Rate": "https://tradingeconomics.com/country-list/interest-rate",
    "Government Debt": "https://tradingeconomics.com/country-list/government-debt-to-gdp",
}
table_class = "table table-hover table-heatmap"

st.sidebar.subheader("Select Economic Indicator to Display")
selected_indicator = st.sidebar.selectbox("Choose an Indicator", list(urls.keys()))

if selected_indicator:
    df = fetch_economic_data(urls[selected_indicator], table_class)
    if df is not None:
        st.subheader(f"📊 {selected_indicator} Data")
        st.write(df.head())

# Fetch news data and visualize sentiment
news_df = scrape_bbc_business_news_rss()
if not news_df.empty:
    st.write(news_df.head())
    
    # Visualize sentiment and indices
    visualize_polarity_distribution(news_df)
    visualize_rag_status_distribution(news_df)
    visualize_fear_index_distribution(news_df)

    # Run machine learning models
    run_ml_models(news_df)

    # Display fear and greed index
    avg_fear_index = news_df['Fear_Index'].mean()
    if avg_fear_index >= 7:
        st.write("Current Market Sentiment: High Fear")
        display_icon("bear_icon.jpg", width=100)
    else:
        st.write("Current Market Sentiment: Greed")
        display_icon("eagle_icon.jpg", width=100)
