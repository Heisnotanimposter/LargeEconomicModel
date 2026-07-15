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

# Sidebar Navigation
st.sidebar.title("🧭 Navigation")
dashboard_view = st.sidebar.radio(
    "Select View",
    ["🌍 Global Interest Rate Ratio Map", "📰 BBC News & Market Sentiment"]
)

if dashboard_view == "🌍 Global Interest Rate Ratio Map":
    st.title("🌍 Global Interest Rate Ratio Map")
    st.markdown("""
    This map visualizes the geographic distribution of **Interest Rate Ratios** across major economies.
    Select different ratio types below to analyze policy divergence, momentum, or real yields.
    """)
    
    # 1. Fetch interest rate data using local scraper with fallback
    with st.spinner("Loading interest rate data..."):
        interest_df = fetch_economic_data(urls["Interest Rate"], table_class)
        if interest_df is None or interest_df.empty:
            from visualizer import load_fallback_csv
            interest_df = load_fallback_csv("Interest_Rate_Data.csv")
            
    if interest_df is None or interest_df.empty:
        st.error("Failed to load interest rate data. Please check connection or verify that 'Interest_Rate_Data.csv' exists.")
    else:
        from visualizer import map_and_expand_countries, plot_world_map_interest_ratio
        
        # Configuration columns
        col1, col2 = st.columns(2)
        
        with col1:
            ratio_type = st.selectbox(
                "Select Ratio Metric",
                [
                    "Ratio to Reference Country",
                    "Tightening Ratio (Current vs. Previous)",
                    "Interest Rate to Inflation Ratio"
                ],
                help="""
                - **Ratio to Reference Country**: Compares interest rates against a selected baseline rate (e.g., US Fed Rate).
                - **Tightening Ratio**: Compares current interest rates against previous rates.
                - **Interest Rate to Inflation Ratio**: Compares interest rates against current inflation rates (indicates real yield coverage).
                """
            )
            
        with col2:
            colorscale_choice = st.selectbox(
                "Select Map Colorscale",
                ["Viridis", "Plasma", "RdYlBu", "Cividis", "Inferno", "Turbo", "Blues"]
            )
            
        # Get mapping of countries to select reference country
        mapped_interest = map_and_expand_countries(interest_df)
        mapped_interest = mapped_interest.dropna(subset=["ISO3", "Last"])
        mapped_interest = mapped_interest.sort_values(by="Country")
        
        ref_countries = []
        for idx, row in mapped_interest.iterrows():
            ref_countries.append((f"{row['Country']} ({row['Last']}%)", row["ISO3"]))
            
        if not ref_countries:
            ref_countries = [("United States (4.5%)", "USA"), ("Euro Area (2.4%)", "DEU"), ("Japan (0.5%)", "JPN")]
            
        ref_iso = None
        if ratio_type == "Ratio to Reference Country":
            ref_selection = st.selectbox(
                "Select Reference Country (Base Rate for Divisor)",
                options=ref_countries,
                format_func=lambda x: x[0]
            )
            if ref_selection:
                ref_iso = ref_selection[1]
                
        # 2. Fetch inflation data if needed
        inflation_df = None
        if ratio_type == "Interest Rate to Inflation Ratio":
            with st.spinner("Loading inflation data..."):
                inflation_df = fetch_economic_data(urls["Inflation Rate"], table_class)
                if inflation_df is None or inflation_df.empty:
                    from visualizer import load_fallback_csv
                    inflation_df = load_fallback_csv("Inflation_Rate_Data.csv")
                    
            if inflation_df is None or inflation_df.empty:
                st.error("Inflation Rate data is required for this metric but could not be loaded.")
                
        # 3. Plot map
        map_data = plot_world_map_interest_ratio(
            interest_df=interest_df,
            inflation_df=inflation_df,
            ratio_type=ratio_type,
            reference_country=ref_iso,
            colorscale=colorscale_choice
        )
        
        # 4. Display Comparison Table
        if map_data is not None and not map_data.empty:
            st.subheader("📊 Ratio Comparison Table")
            
            # Display sorted by Ratio descending
            display_df = map_data.copy().sort_values(by="Ratio", ascending=False)
            
            # Select columns
            cols_to_show = ["Country", "ISO3", "Interest Rate (%)", "Previous Interest Rate (%)"]
            if "Inflation Rate (%)" in display_df.columns:
                cols_to_show.append("Inflation Rate (%)")
            cols_to_show.append("Ratio")
            
            display_df = display_df[cols_to_show].reset_index(drop=True)
            
            # Custom styling
            display_df["Ratio"] = display_df["Ratio"].map(lambda x: f"{x:.4f}x" if pd.notnull(x) else "N/A")
            
            st.dataframe(display_df, use_container_width=True)

else:  # Legacy view: BBC News & Sentiment Analysis
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
        # Example data for z-axis
        z_values = news_df['Fear_Index']
        
        # Define fig_3d before updating layout
        fig_3d = go.Figure(data=[go.Scatter3d(
            x=news_df['Polarity'],
            y=news_df['Subjectivity'],
            z=z_values,
            mode='markers',
            marker=dict(
                size=10,
                color=z_values,
                colorscale='Viridis',  # You can modify the color scale here
                opacity=0.8
            )
        )])
        
        # Now you can update the layout for fig_3d
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
        
        # Display the 3D plot in Streamlit
        st.plotly_chart(fig_3d, use_container_width=True)
        
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

    if not news_df.empty:
        csv = convert_df(news_df)
        st.download_button(
            label="📥 Download News Sentiment Analysis Data as CSV",
            data=csv,
            file_name='news_sentiment_analysis.csv',
            mime='text/csv',
        )
