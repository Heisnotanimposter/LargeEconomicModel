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

# Custom CSS for enhancing visuals
st.markdown("""
    <style>
    .main {
        background-color: #f4f4f4;
    }
    .sidebar .sidebar-content {
        background-color: #fafafa;
    }
    .st-dp {
        border-radius: 10px;
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to display images
def display_icon(icon_path, width=50):
    try:
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'<img src="data:image/png;base64,{encoded_string}" width="{width}">', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Icon not found at: {icon_path}")

# Function to fetch economic data with error handling
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

# URLs of the pages to scrape data from
urls = {
    "GDP": "https://tradingeconomics.com/country-list/gdp",
    "Inflation Rate": "https://tradingeconomics.com/country-list/inflation-rate",
    "Unemployment Rate": "https://tradingeconomics.com/country-list/unemployment-rate",
    "Interest Rate": "https://tradingeconomics.com/country-list/interest-rate",
    "Government Debt": "https://tradingeconomics.com/country-list/government-debt-to-gdp",
}

# Table class used on TradingEconomics website
table_class = "table table-hover table-heatmap"

# Title and description
st.title("🌐 Economic Data & Sentiment Analysis")
st.markdown("Analyze the economic indicators and sentiment analysis from BBC News with AI-powered models.")

# Fetch data for each economic indicator
st.sidebar.subheader("Select Economic Indicator to Display")
selected_indicator = st.sidebar.selectbox("Choose an Indicator", list(urls.keys()))

if selected_indicator:
    df = fetch_economic_data(urls[selected_indicator], table_class)
    if df is not None:
        st.subheader(f"📊 {selected_indicator} Data")
        st.write(df.head())
    else:
        st.write(f"Failed to scrape data for {selected_indicator}")

# Function to scrape BBC business news and perform sentiment analysis with error handling
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

# Sentiment and fear index calculations
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

if not news_df.empty:
    st.write(news_df.head())

    # Visualize sentiment polarity distribution
    fig = px.histogram(news_df, x='Polarity', nbins=20, title='Sentiment Polarity Distribution', template='plotly_dark')
    st.plotly_chart(fig)

    # Create a binary target variable
    news_df['Sentiment'] = news_df['Polarity'].apply(lambda x: 1 if x >= 0 else 0)

    # Create a RAG status based on sentiment polarity
    news_df['RAG_Status'] = news_df['Polarity'].apply(lambda x: 'Green' if x > 0.1 else 'Red' if x < -0.1 else 'Amber')

    # Calculate the fear index
    news_df['Fear_Index'] = news_df.apply(lambda row: calculate_fear_index(row['Polarity'], row['Subjectivity']), axis=1)

    # Visualize RAG status distribution
    fig = px.histogram(news_df, x='RAG_Status', color='RAG_Status', title='RAG Status Distribution', template='plotly_dark')
    st.plotly_chart(fig)

    # Visualize Fear Index distribution
    fig = px.histogram(news_df, x='Fear_Index', nbins=10, title='Fear Index Distribution', template='plotly_dark')
    st.plotly_chart(fig)

    # Prepare features and target variable for machine learning
    X = news_df[['Polarity', 'Subjectivity', 'Fear_Index']]
    y = news_df['Sentiment']

    if not X.empty and not y.empty:
        st.write(news_df['Sentiment'].value_counts())

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        st.write(pd.Series(y_train).value_counts())

        # Initialize and train the logistic regression model
        model = LogisticRegression()
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Evaluate the model
        accuracy = accuracy_score(y_test, y_pred)
        st.write(f'Logistic Regression Accuracy: {accuracy}')

        # Display feature importances for Random Forest (if applicable)
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        rf_feature_importances = pd.Series(rf_model.feature_importances_, index=X.columns)
        fig, ax = plt.subplots()
        rf_feature_importances.nlargest(3).plot(kind='barh', ax=ax)
        plt.title('Random Forest Feature Importances')
        st.pyplot(fig)

# End of analysis
st.subheader("End of Analysis")
