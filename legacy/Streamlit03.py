import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ml_models import run_ml_models
from news_sentiment import scrape_bbc_business_news_rss as scrape_bbc_news_sentiment, calculate_fear_index
from economic_data import fetch_economic_data
from visualizer import plot_3d_rag_model, map_and_expand_countries, plot_world_map_interest_ratio, load_fallback_csv
from utils import display_icon
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression  # Added missing import to fix NameError!

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
    
    # 1. Fetch interest rate data
    with st.spinner("Loading interest rate data..."):
        interest_df = fetch_economic_data("Interest Rate")
        if interest_df is None or interest_df.empty:
            interest_df = load_fallback_csv("Interest_Rate_Data.csv")
            
    if interest_df is None or interest_df.empty:
        st.error("Failed to load interest rate data. Please check connection or verify that 'Interest_Rate_Data.csv' exists.")
    else:
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
                inflation_df = fetch_economic_data("Inflation Rate")
                if inflation_df is None or inflation_df.empty:
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
    # Sidebar indicator select
    st.sidebar.subheader("Select Economic Indicator to Display")
    selected_indicator = st.sidebar.selectbox("Choose an Indicator", list(urls.keys()))

    if selected_indicator:
        df = fetch_economic_data(selected_indicator)
        if df is not None:
            st.subheader(f"📊 {selected_indicator} Data")
            st.dataframe(df)
            st.write("The above table shows the latest values for the selected economic indicator.")
        else:
            st.write(f"Failed to scrape data for {selected_indicator}")

    # Scrape BBC business news and perform sentiment analysis
    news_df = scrape_bbc_news_sentiment()

    # Drop rows with neutral sentiment (Polarity == 0 and Subjectivity == 0)
    if not news_df.empty:
        news_df = news_df[(news_df['Polarity'] != 0) | (news_df['Subjectivity'] != 0)]

    # Ensure we have at least 100 rows
    if news_df.empty or len(news_df) < 100:
        st.warning("Insufficient news data. BBC news stream has fewer than 100 active sentiment headlines.")
        if not news_df.empty:
            st.subheader("📰 BBC Business News Headlines (Partial Data)")
            st.write(news_df.head(20))
    else:
        # Calculate Fear Index
        news_df['Fear_Index'] = news_df.apply(lambda row: calculate_fear_index(row['Polarity'], row['Subjectivity']), axis=1)

        st.subheader("📰 BBC Business News Headlines")
        st.write(news_df.head())

        # Visualize Fear Index with a 3D plot
        color_scheme = st.sidebar.selectbox('Select Color Scheme', ['Viridis', 'Cividis', 'Plasma'])

        # Time series component for 3D Plot
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

    # Download option for news sentiment analysis data if news_df is not empty
    if not news_df.empty:
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
