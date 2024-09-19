# rag_visualizer.py
import streamlit as st
from economic_data import fetch_economic_data
from news_sentiment import scrape_bbc_business_news_rss, calculate_fear_index
from visualizer import plot_rag_status, plot_fear_index, plot_3d_rag_model
from ml_models import run_ml_models
import os

# Page Configuration
st.set_page_config(page_title="Economic News & Sentiment Analysis", layout="wide")

st.title("🌐 Economic Data & Sentiment Analysis")
st.markdown("Analyze economic indicators and sentiment analysis from BBC News with AI-powered models.")

# Section 1: Economic Data Analysis
st.sidebar.subheader("Economic Indicator")
selected_indicator = st.sidebar.selectbox("Select an Indicator", ["GDP", "Inflation Rate", "Unemployment Rate", "Interest Rate", "Government Debt"])
economic_data = fetch_economic_data(selected_indicator)
if economic_data is not None:
    st.subheader(f"{selected_indicator} Data")
    st.write(economic_data)

# Section 2: BBC News Sentiment Analysis
st.sidebar.subheader("News Sentiment Analysis")
news_df = scrape_bbc_business_news_rss()
if not news_df.empty:
    st.subheader("BBC News Headlines Sentiment Analysis")
    st.write(news_df.head())
    
    # Visualization
    plot_rag_status(news_df)
    plot_fear_index(news_df)
    
    # 3D RAG Model Visualization
    st.sidebar.subheader("RAG Model 3D Settings")
    color_choice = st.sidebar.selectbox("Choose a color palette", ["Red", "Green", "Amber"])
    plot_3d_rag_model(news_df, color_choice)

    # Run Machine Learning Models
    run_ml_models(news_df)
else:
    st.warning("No news data available.")

# End of App
st.subheader("End of Analysis")
st.write("Thank you for using the Economic Data Analysis and Sentiment Analysis tool!")