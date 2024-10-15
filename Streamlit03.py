import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ml_models import train_models, evaluate_models
from news_sentiment import scrape_bbc_news_sentiment, calculate_fear_index
from economic_data import fetch_economic_data
from visualizer import plot_3d_rag_model
from utils import display_icon
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Page Configuration
st.set_page_config(page_title="Economic News & Sentiment Analysis", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for enhanced visuals and readability
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .st-dp {
        border-radius: 10px;
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# URLs for different economic indicators
urls = {
    "GDP": "https://tradingeconomics.com/country-list/gdp",
    "Inflation Rate": "https://tradingeconomics.com/country-list/inflation-rate",
    "Unemployment Rate": "https://tradingeconomics.com/country-list/unemployment-rate",
    "Interest Rate": "https://tradingeconomics.com/country-list/interest-rate",
    "Government Debt": "https://tradingeconomics.com/country-list/government-debt-to-gdp",
}

# Sidebar configuration to select economic indicators
st.sidebar.subheader("Select Economic Indicator to Display")
selected_indicator = st.sidebar.selectbox("Choose an Indicator", list(urls.keys()))

if selected_indicator:
    df = fetch_economic_data(urls[selected_indicator])
    if df is not None:
        st.subheader(f"📊 {selected_indicator} Data")
        st.dataframe(df)
        st.write("The above table shows the latest values for the selected economic indicator.")
    else:
        st.write(f"Failed to scrape data for {selected_indicator}")

# Scrape BBC business news and perform sentiment analysis
news_df = scrape_bbc_news_sentiment()

# Drop rows with neutral sentiment (Polarity == 0 and Subjectivity == 0)
news_df = news_df[(news_df['Polarity'] != 0) | (news_df['Subjectivity'] != 0)]

# Ensure we have at least 100 rows
if len(news_df) < 100:
    st.warning("Insufficient data. Please try again later.")
else:
    # Calculate Fear Index
    news_df['Fear_Index'] = news_df.apply(lambda row: calculate_fear_index(row['Polarity'], row['Subjectivity']), axis=1)

    st.subheader("📰 BBC Business News Headlines")
    st.write(news_df.head())

    # Visualize Fear Index with a 3D plot
    color_scheme = st.sidebar.selectbox('Select Color Scheme', ['Viridis', 'Cividis', 'Plasma'])

    # Time series component for 3D Plot (assuming each headline represents a point in time)
    news_df['Time'] = pd.date_range(start='2023-01-01', periods=len(news_df), freq='D')

    plot_3d_rag_model(news_df, color_scheme)

    # Model training and evaluation
    X = news_df[['Polarity', 'Subjectivity', 'Fear_Index']]
    y = news_df['Polarity'].apply(lambda x: 1 if x >= 0 else 0)

    if not X.empty:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LogisticRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        st.write(f"Model Accuracy: {accuracy}")

    # End of analysis
    st.subheader("Analysis Complete")

# Download option for news sentiment analysis data
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(news_df)
st.download_button(
    label="📥 Download News Sentiment Analysis Data as CSV",
    data=csv,
    file_name='news_sentiment_analysis.csv',
    mime='text/csv',
)
