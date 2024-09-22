import streamlit as st
import pandas as pd
from economic_data import fetch_economic_data
from news_sentiment import scrape_bbc_business_news_rss
from visualizer import plot_rag_status, plot_fear_index, plot_3d_rag_model
from ml_models import run_ml_models

# Configure the Streamlit page with a more informative description
st.set_page_config(
    page_title="Economic Data & Sentiment Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set a custom CSS style for improved readability
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .sidebar .sidebar-content {
        background-color: #f1f1f1;
        border-radius: 5px;
        padding: 15px;
    }
    h1, h2, h3 {
        font-family: 'Arial', sans-serif;
    }
    .st-dp {
        border-radius: 10px;
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.title("🌍 Economic Data & Market Sentiment Analysis")
st.write(
    """
    Welcome to the Economic Data Analysis dashboard. Here, you can explore key economic indicators, 
    analyze sentiment from global business news, and gain insights into market trends with AI-powered 
    models. Use the sidebar to navigate and customize your analysis.
    """
)

# Sidebar for user interaction
st.sidebar.header("Select Analysis")

# Section 1: Fetch Economic Data (GDP, Inflation, Unemployment, etc.)
st.sidebar.subheader("Select Economic Indicator to Display")
selected_indicator = st.sidebar.selectbox("Choose an Indicator", ["GDP", "Inflation Rate", "Unemployment Rate", "Interest Rate", "Government Debt"])

# Fetch and display the selected economic indicator
st.subheader(f"📊 {selected_indicator} Data")
st.write("Visualizing key economic indicators for comprehensive analysis.")
economic_data = fetch_economic_data(selected_indicator)
if economic_data is not None:
    st.write(economic_data.head())
else:
    st.error(f"Failed to load data for {selected_indicator}. Please try again.")

# Section 2: BBC News Sentiment Analysis
st.sidebar.subheader("News Sentiment Analysis")
st.write("Analyzing market sentiment based on headlines from BBC Business News.")

# Scrape news headlines and analyze sentiment
news_df = scrape_bbc_business_news_rss()
if not news_df.empty:
    st.subheader("📰 BBC News Headlines Sentiment Analysis")
    st.write("Analyzed sentiment from the latest BBC Business News articles.")
    st.write(news_df.head())

    # Sentiment polarity distribution visualization
    st.subheader("Sentiment Polarity Distribution")
    st.write("This chart shows the distribution of sentiment polarity across the collected headlines.")
    plot_rag_status(news_df)

    # Fear Index visualization
    st.subheader("Fear Index Distribution")
    st.write(
        """
        The Fear Index quantifies the level of concern in the market. Higher values indicate a stronger
        fear sentiment, which could signal market instability.
        """
    )
    plot_fear_index(news_df)

    # 3D RAG Model Visualization (User-Controlled)
    st.sidebar.subheader("3D RAG Model Settings")
    color_choice = st.sidebar.color_picker("Select Color Scheme", "#FF6347")
    st.subheader("3D Visualization of Market Sentiment with Fear Index")
    plot_3d_rag_model(news_df, color_choice)

    # Section 3: Run AI-powered Machine Learning Models
    st.subheader("AI-Powered Sentiment Prediction")
    st.write(
        """
        Here we run various machine learning models to predict market sentiment based on
        historical data and trends. You can compare the performance of different models
        such as Logistic Regression, Random Forest, and Gradient Boosting.
        """
    )
    run_ml_models(news_df)
else:
    st.warning("No news data available for sentiment analysis. Please try again later.")

# Footer Section with Download Option
st.subheader("Download Data")
st.write(
    """
    You can download the analyzed sentiment data as a CSV file for further analysis. 
    Use it to keep track of market sentiment and make informed decisions.
    """
)

# Provide download option for sentiment data
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

if not news_df.empty:
    csv_data = convert_df_to_csv(news_df)
    st.download_button(
        label="Download Sentiment Data as CSV",
        data=csv_data,
        file_name='news_sentiment_analysis.csv',
        mime='text/csv'
    )

# End of Analysis
st.subheader("Thank you for using the Economic Data & Market Sentiment Analysis Tool!")
st.write("Stay informed and make data-driven decisions for better financial outcomes.")
