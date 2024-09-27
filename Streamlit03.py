import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from textblob import TextBlob
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xml.etree.ElementTree as ET
import base64

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

# Helper function to display images
@st.cache_data
def display_icon(icon_path, width=50):
    try:
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'<img src="data:image/png;base64,{encoded_string}" width="{width}">', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Icon not found at: {icon_path}")

# Fetch economic data from TradingEconomics with error handling
@st.cache_data(show_spinner=False)
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

# URLs for different economic indicators
urls = {
    "GDP": "https://tradingeconomics.com/country-list/gdp",
    "Inflation Rate": "https://tradingeconomics.com/country-list/inflation-rate",
    "Unemployment Rate": "https://tradingeconomics.com/country-list/unemployment-rate",
    "Interest Rate": "https://tradingeconomics.com/country-list/interest-rate",
    "Government Debt": "https://tradingeconomics.com/country-list/government-debt-to-gdp",
}

# Table class for scraping data
table_class = "table table-hover table-heatmap"

# Title and description for the application
st.title("🌐 Economic Data & Sentiment Analysis")
st.markdown("""
This app provides a high-level overview of economic indicators such as GDP, Inflation, Unemployment Rate, Interest Rates, and more.
Additionally, it performs sentiment analysis on financial news to help assess market trends.
""")

# Fetch and display economic data
st.sidebar.subheader("Select Economic Indicator to Display")
selected_indicator = st.sidebar.selectbox("Choose an Indicator", list(urls.keys()))

if selected_indicator:
    df = fetch_economic_data(urls[selected_indicator], table_class)
    if df is not None:
        st.subheader(f"📊 {selected_indicator} Data")
        st.dataframe(df)
        st.write("The above table shows the latest values for the selected economic indicator.")
    else:
        st.write(f"Failed to scrape data for {selected_indicator}")

# Function to scrape BBC business news and perform sentiment analysis
@st.cache_data(show_spinner=False)
def scrape_bbc_business_news_rss():
    try:
        rss_url = "http://feeds.bbci.co.uk/news/business/rss.xml"
        response = requests.get(rss_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        headlines = []
        for item in root.findall('.//item')[:100]:  # Fetch at least 100 headlines
            title = item.find('title').text
            if title:
                headlines.append(title)

        if not headlines:
            st.warning("No headlines found.")
            return pd.DataFrame()

        data = []
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

# Function to calculate fear index
def calculate_fear_index(polarity, subjectivity):
    if polarity < -0.3 and subjectivity > 0.5:
        return 10  # High fear
    elif polarity < -0.2:
        return 7  # Moderate fear
    elif polarity < -0.1:
        return 4  # Low fear
    else:
        return 1  # No fear

# Scrape news headlines and perform sentiment analysis
news_df = scrape_bbc_business_news_rss()

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
    z_values = news_df['Fear_Index']
    color_scheme = st.sidebar.selectbox('Select Color Scheme', ['Viridis', 'Cividis', 'Plasma'])

    # Time series component for 3D Plot (assuming each headline represents a point in time)
    news_df['Time'] = pd.date_range(start='2023-01-01', periods=len(news_df), freq='D')

    fig_3d = go.Figure(data=[go.Scatter3d(
        x=news_df['Polarity'],
        y=news_df['Subjectivity'],
        z=news_df['Time'].astype(str),  # Add time component
        mode='markers',
        marker=dict(
            size=10,
            color=z_values,
            colorscale=color_scheme,
            opacity=0.8
        )
    )])

    fig_3d.update_layout(
        title="3D Fear & Greed Index with Time Series",
        scene=dict(
            xaxis_title='Polarity',
            yaxis_title='Subjectivity',
            zaxis_title='Date',
        )
    )

    st.plotly_chart(fig_3d)

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
