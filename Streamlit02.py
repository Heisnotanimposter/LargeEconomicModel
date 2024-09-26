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
    """
    Fetches economic data from TradingEconomics and returns a DataFrame.
    """
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

# URLs for different economic indicators, including Unemployment Rate and Interest Rates
urls = {
    "GDP": "https://tradingeconomics.com/country-list/gdp",
    "Inflation Rate": "https://tradingeconomics.com/country-list/inflation-rate",
    "Unemployment Rate": "https://tradingeconomics.com/country-list/unemployment-rate",
    "Interest Rate": "https://tradingeconomics.com/country-list/interest-rate",
    "Government Debt": "https://tradingeconomics.com/country-list/government-debt-to-gdp",
    "Fed Interest Rate": "https://www.federalreserve.gov/releases/h15/"
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
    """
    Fetches BBC business news via RSS feed and returns a DataFrame with sentiment analysis.
    """
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

# Function to calculate fear index
def calculate_fear_index(polarity, subjectivity):
    """
    Calculates a fear index based on sentiment polarity and subjectivity.
    """
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

# Display sentiment analysis results
if not news_df.empty:
    st.subheader("📰 BBC Business News Sentiment Analysis")
    st.write("The table below shows the sentiment analysis results of recent financial news headlines.")
    st.write(news_df.head())

    # Visualize sentiment polarity distribution
    fig = px.histogram(news_df, x='Polarity', nbins=20, title='Sentiment Polarity Distribution', template='plotly_white')
    st.plotly_chart(fig)

    # Create binary sentiment variable and classify RAG status
    news_df['Sentiment'] = news_df['Polarity'].apply(lambda x: 1 if x >= 0 else 0)
    news_df['RAG_Status'] = news_df['Polarity'].apply(lambda x: 'Green' if x > 0.1 else 'Red' if x < -0.1 else 'Amber')

    # Calculate fear index
    news_df['Fear_Index'] = news_df.apply(lambda row: calculate_fear_index(row['Polarity'], row['Subjectivity']), axis=1)

    # Visualize RAG status and Fear Index distribution
    st.subheader("Market Sentiment Overview")
    fig = px.histogram(news_df, x='RAG_Status', color='RAG_Status', title='RAG Status Distribution', template='plotly_white')
    st.plotly_chart(fig)

    fig = px.histogram(news_df, x='Fear_Index', nbins=10, title='Fear Index Distribution', template='plotly_white')
    st.plotly_chart(fig)

    # Add time-based interactive 3D graph models
    st.subheader("🧭 Time-based 3D Interactive Visualization")
    
    color_scheme = st.sidebar.selectbox("Select Color Scheme", ['Viridis', 'Plasma', 'Cividis', 'Inferno'])
    z_values = news_df['Fear_Index'].values
    
    fig_3d.update_layout(
        title="3D Interactive Visualization of Sentiment Analysis",
        scene=dict(
            xaxis_title="Polarity",
            yaxis_title="Subjectivity",
            zaxis_title="Fear Index",
            xaxis=dict(backgroundcolor="rgb(200, 200, 230)", gridcolor="white"),
            yaxis=dict(backgroundcolor="rgb(230, 200,230)", gridcolor="white"),
            zaxis=dict(backgroundcolor="rgb(230, 230,200)", gridcolor="white"),
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        hovermode="closest",
    )
    
    st.plotly_chart(fig_3d, use_container_width=True)

    # Model training and evaluation
    st.subheader("📊 Sentiment Classification Using Machine Learning")

    # Prepare features and target variable
    X = news_df[['Polarity', 'Subjectivity', 'Fear_Index']]
    y = news_df['Sentiment']

    if not X.empty and not y.empty:
        st.write("Sentiment Distribution")
        st.write(pd.Series(y).value_counts())

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # Train logistic regression model
        model = LogisticRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Display accuracy and classification report
        accuracy = accuracy_score(y_test, y_pred)
        st.write(f'Logistic Regression Accuracy: {accuracy}')

        report = classification_report(y_test, y_pred, output_dict=True)
        st.write(pd.DataFrame(report).transpose())

        # Visualize confusion matrix
        conf_matrix = confusion_matrix(y_test, y_pred)
        fig, ax = plt.subplots()
        sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', ax=ax)
        plt.title('Confusion Matrix for Logistic Regression')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        st.pyplot(fig)

        # Initialize Random Forest and Gradient Boosting models
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)

        # Train the models
        rf_model.fit(X_train, y_train)
        gb_model.fit(X_train, y_train)

        # Predictions and evaluations
        rf_pred = rf_model.predict(X_test)
        gb_pred = gb_model.predict(X_test)

        rf_accuracy = accuracy_score(y_test, rf_pred)
        gb_accuracy = accuracy_score(y_test, gb_pred)

        st.write(f'Random Forest Accuracy: {rf_accuracy}')
        st.write(f'Gradient Boosting Accuracy: {gb_accuracy}')

        # Feature importance for Random Forest
        rf_feature_importances = pd.Series(rf_model.feature_importances_, index=X.columns)
        fig, ax = plt.subplots()
        rf_feature_importances.nlargest(3).plot(kind='barh', ax=ax)
        plt.title('Random Forest Feature Importances')
        st.pyplot(fig)

        # Voting Classifier
        voting_model = VotingClassifier(estimators=[('rf', rf_model), ('gb', gb_model)], voting='soft')
        voting_model.fit(X_train, y_train)
        voting_pred = voting_model.predict(X_test)

        # Voting classifier evaluation
        voting_accuracy = accuracy_score(y_test, voting_pred)
        voting_report = classification_report(y_test, voting_pred, output_dict=True)

        st.write(f'Voting Classifier Accuracy: {voting_accuracy}')
        st.write(pd.DataFrame(voting_report).transpose())

        # Plot accuracy comparison
        st.subheader("📊 Model Accuracy Comparison")
        models = ['Logistic Regression', 'Random Forest', 'Gradient Boosting', 'Voting Classifier']
        accuracies = [accuracy, rf_accuracy, gb_accuracy, voting_accuracy]

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=models, y=accuracies, ax=ax)
        ax.set_title('Model Accuracy Comparison')
        ax.set_xlabel('Model')
        ax.set_ylabel('Accuracy')
        ax.set_ylim(0, 1)
        st.pyplot(fig)

# End of analysis
st.subheader("📈 End of Analysis")
st.write("Thank you for using the Economic Data & Sentiment Analysis Tool!")

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

