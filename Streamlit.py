import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from mpl_toolkits.mplot3d import Axes3D
from textblob import TextBlob
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xml.etree.ElementTree as ET

# Page Configuration
st.set_page_config(page_title="Economic News Analysis", layout="wide")

# Function to fetch economic data
def fetch_economic_data(url, table_class):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
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

st.title("Economic Data Analysis and Sentiment Analysis")

# Fetch data for each economic indicator
economic_data = {}
for indicator, url in urls.items():
    df = fetch_economic_data(url, table_class)
    if df is not None:
        economic_data[indicator] = df
        st.write(f"Data for {indicator} successfully scraped!")
        st.write(df.head())
    else:
        st.write(f"Failed to scrape data for {indicator}")

# Function to scrape BBC business news and perform sentiment analysis using RSS feed
def scrape_bbc_business_news_rss():
    rss_url = "http://feeds.bbci.co.uk/news/business/rss.xml"
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)

    headlines = []
    for item in root.findall('.//item'):
        title = item.find('title').text
        if title:
            headlines.append(title)

    if not headlines:
        st.warning("No headlines found. Exiting the script.")
        return pd.DataFrame()

    data = []
    for headline in headlines:
        sentiment = TextBlob(headline).sentiment
        data.append([headline, sentiment.polarity, sentiment.subjectivity])

    df = pd.DataFrame(data, columns=['Headline', 'Polarity', 'Subjectivity'])
    return df

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

# Check if the dataset is empty before proceeding
if news_df.empty:
    st.warning("The dataset is empty. Exiting the script.")
else:
    st.write(news_df.head())

    # Visualize sentiment polarity distribution
    fig = px.histogram(news_df, x='Polarity', nbins=20, title='Sentiment Polarity Distribution')
    st.plotly_chart(fig)

    # Create a binary target variable
    news_df['Sentiment'] = news_df['Polarity'].apply(lambda x: 1 if x >= 0 else 0)

    # Create a RAG status based on sentiment polarity
    def classify_sentiment(polarity):
        if polarity > 0.1:
            return 'Green'  # Positive sentiment
        elif polarity < -0.1:
            return 'Red'    # Negative sentiment
        else:
            return 'Amber'  # Neutral sentiment

    news_df['RAG_Status'] = news_df['Polarity'].apply(classify_sentiment)
    
    # Calculate the fear index
    news_df['Fear_Index'] = news_df.apply(lambda row: calculate_fear_index(row['Polarity'], row['Subjectivity']), axis=1)

    # Visualize RAG status distribution
    fig = px.histogram(news_df, x='RAG_Status', color='RAG_Status', title='RAG Status Distribution')
    st.plotly_chart(fig)

    # Visualize Fear Index distribution
    fig = px.histogram(news_df, x='Fear_Index', nbins=10, title='Fear Index Distribution')
    st.plotly_chart(fig)

    # Prepare features and target variable for machine learning
    X = news_df[['Polarity', 'Subjectivity', 'Fear_Index']]
    y = news_df['Sentiment']

    # Ensure we have data before proceeding
    if X.empty or y.empty:
        st.warning("Features or target variable is empty. Exiting the script.")
    else:
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Initialize and train the logistic regression model
        model = LogisticRegression()
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Evaluate the model
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)

        st.write(f'Logistic Regression Accuracy: {accuracy}')
        st.write(pd.DataFrame(report).transpose())

        # Plot confusion matrix
        conf_matrix = confusion_matrix(y_test, y_pred)
        fig, ax = plt.subplots()
        sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', ax=ax)
        plt.title('Confusion Matrix for Logistic Regression')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        st.pyplot(fig)

        # Initialize the Random Forest and Gradient Boosting models
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)

        # Train the models
        rf_model.fit(X_train, y_train)
        gb_model.fit(X_train, y_train)

        # Make predictions with both models
        rf_pred = rf_model.predict(X_test)
        gb_pred = gb_model.predict(X_test)

        # Evaluate the models
        rf_accuracy = accuracy_score(y_test, rf_pred)
        gb_accuracy = accuracy_score(y_test, gb_pred)

        st.write(f'Random Forest Accuracy: {rf_accuracy}')
        st.write(f'Gradient Boosting Accuracy: {gb_accuracy}')

        # Plot feature importances for Random Forest
        rf_feature_importances = pd.Series(rf_model.feature_importances_, index=X.columns)
        fig, ax = plt.subplots()
        rf_feature_importances.nlargest(3).plot(kind='barh', ax=ax)
        plt.title('Random Forest Feature Importances')
        st.pyplot(fig)

        # Create a voting classifier that combines both models
        voting_model = VotingClassifier(estimators=[('rf', rf_model), ('gb', gb_model)], voting='soft')
        voting_model.fit(X_train, y_train)
        voting_pred = voting_model.predict(X_test)


        # Evaluate the voting model
        voting_accuracy = accuracy_score(y_test, voting_pred)
        voting_report = classification_report(y_test, voting_pred, output_dict=True)

        st.write(f'Voting Classifier Accuracy: {voting_accuracy}')
        st.write(pd.DataFrame(voting_report).transpose())

        # Plot accuracy comparison
        models = ['Logistic Regression', 'Random Forest', 'Gradient Boosting', 'Voting Classifier']
        accuracies = [accuracy, rf_accuracy, gb_accuracy, voting_accuracy]

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=models, y=accuracies, ax=ax)
        ax.set_title('Model Accuracy Comparison')
        ax.set_xlabel('Model')
        ax.set_ylabel('Accuracy')
        ax.set_ylim(0, 1)
        st.pyplot(fig)

        # 3D plot of the RAG model with Fear Index
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        colors = news_df['RAG_Status'].map({'Red': 'r', 'Amber': 'orange', 'Green': 'g'}).tolist()
        ax.scatter(news_df['Polarity'], news_df['Subjectivity'], news_df['Fear_Index'], c=colors, s=50)

        ax.set_xlabel('Polarity')
        ax.set_ylabel('Subjectivity')
        ax.set_zlabel('Fear Index')
        ax.set_title('3D Visualization of RAG Model with Fear Index')

        st.pyplot(fig)

        # Add interactive components for better user experience
        st.sidebar.header('User Input Features')
        selected_model = st.sidebar.selectbox('Select Model', models)

        st.subheader('Prediction Results')
        if selected_model == 'Logistic Regression':
            st.write(f'Logistic Regression Accuracy: {accuracy}')
            st.write(pd.DataFrame(report).transpose())
        elif selected_model == 'Random Forest':
            st.write(f'Random Forest Accuracy: {rf_accuracy}')
            st.write(pd.DataFrame(rf_report).transpose())
        elif selected_model == 'Gradient Boosting':
            st.write(f'Gradient Boosting Accuracy: {gb_accuracy}')
            st.write(pd.DataFrame(gb_report).transpose())
        else:
            st.write(f'Voting Classifier Accuracy: {voting_accuracy}')
            st.write(pd.DataFrame(voting_report).transpose())

        st.subheader('End of Analysis')
        st.write("Thank you for using the Economic Data Analysis and Sentiment Analysis tool!")

        # Provide download options for the data
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df(news_df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='news_sentiment_analysis.csv',
            mime='text/csv',
        )

# Run Streamlit app locally
# You can run this script using: streamlit run app.py