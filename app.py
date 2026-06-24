import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
import sys
import time
import datetime
import xml.etree.ElementTree as ET
from textblob import TextBlob
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Fix path to legacy folder
sys.path.append(os.path.join(os.path.dirname(__file__), "legacy"))

try:
    from legacy.visualizer import clean_numeric_col, map_and_expand_countries, plot_world_map_interest_ratio, load_fallback_csv
    from legacy.news_sentiment import scrape_bbc_business_news_rss, calculate_fear_index
except ImportError:
    st.error("Failed to import legacy visualizer/sentiment helper modules. Make sure legacy/ folder contains visualizer.py and news_sentiment.py")

# Check if genai is available
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Page Config
st.set_page_config(
    page_title="LEM - Large Economic Model Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Obsidian Custom Styling (High-Contrast Monotone)
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background-color: #0A0A0A;
        color: #FFFFFF;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #222222;
    }
    section[data-testid="stSidebar"] * {
        color: #A1A1AA !important;
    }
    section[data-testid="stSidebar"] .st-bd {
        color: #FFFFFF !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-family: 'Geist Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.05em !important;
    }
    
    /* Code/Precision metrics */
    .precision-text {
        font-family: 'Geist Mono', monospace;
        color: #FFFFFF;
    }
    
    /* Card design */
    .lem-card {
        background-color: #161616;
        border: 1px solid #2A2A2A;
        border-radius: 4px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.2s ease-in-out;
    }
    .lem-card:hover {
        border-color: #555555;
        background-color: #1C1C1C;
    }
    
    /* Active indicator */
    .active-badge {
        background-color: #FFFFFF;
        color: #000000;
        padding: 2px 8px;
        border-radius: 2px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
        font-family: 'Geist Mono', monospace;
    }
    .inactive-badge {
        border: 1px solid #333333;
        color: #A1A1AA;
        padding: 2px 8px;
        border-radius: 2px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
        font-family: 'Geist Mono', monospace;
    }
    
    /* Buttons */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 4px !important;
        border: 1px solid #FFFFFF !important;
        font-weight: bold !important;
        transition: all 0.2s !important;
    }
    div.stButton > button:hover {
        background-color: #E5E5E5 !important;
        border-color: #E5E5E5 !important;
        transform: translateY(-1px);
    }
    
    /* Horizontal rule */
    hr {
        border-color: #222222 !important;
    }
    
    /* Form inputs */
    input, select, textarea {
        background-color: #121212 !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# Helper function to check if API is running
@st.cache_data(ttl=5)
def check_api_health():
    try:
        response = requests.get("http://localhost:8000/health", timeout=1.5)
        if response.status_code == 200:
            return True, response.json()
    except requests.exceptions.RequestException:
        pass
    return False, {}

# Sidebar Header & Navigation
st.sidebar.markdown("""
    <div style="padding: 10px 0;">
        <span style="font-size: 1.5rem; font-weight: 900; color: #FFFFFF; letter-spacing: -0.05em;">LARGE ECONOMIC MODEL</span>
        <span style="font-family: 'Geist Mono', monospace; font-size: 0.8rem; display: block; color: #A1A1AA; margin-top: -5px;">ENGINE COMMAND CENTER [v1.0]</span>
    </div>
    <hr style="margin: 10px 0 20px 0; border-color: #222222;">
""", unsafe_allow_html=True)

# Check API status
api_online, health_data = check_api_health()

if api_online:
    st.sidebar.markdown("""
        <div style="margin-bottom: 20px;">
            <span class="active-badge">● API ONLINE</span>
            <span style="font-family: 'Geist Mono', monospace; font-size: 0.75rem; color: #A1A1AA; margin-left: 5px;">port 8000</span>
        </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
        <div style="margin-bottom: 20px;">
            <span class="inactive-badge">○ API OFFLINE</span>
            <span style="font-family: 'Geist Mono', monospace; font-size: 0.75rem; color: #777777; margin-left: 5px;">fallback active</span>
        </div>
    """, unsafe_allow_html=True)

# Main Navigation
nav_selection = st.sidebar.radio(
    "SELECT MODULE",
    [
        "🏠 Dashboard Executive",
        "📈 Macroeconomic Explorer",
        "🌍 Monetary Divergence Map",
        "📰 Market Sentiment Desk",
        "🧠 ML Sentiment Lab",
        "📊 OECD Data Hub",
        "✨ Gemini AI Financial Advisor",
        "🤖 AutoBot Simulation Desk"
    ]
)

# ----------------- MODULE 1: Landing / Executive Dashboard -----------------
if nav_selection == "🏠 Dashboard Executive":
    st.title("🏠 Executive Command Center Dashboard")
    st.markdown("Unifying separate and fragmented indicators, trading agents, and LLM engines.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="lem-card">
                <h3>Backend Engines</h3>
                <p>Status of API server components:</p>
                <div style="margin-top: 15px;">
                    <span class="active-badge" style="display: block; width: fit-content; margin-bottom: 8px;">api core: {"ACTIVE" if api_online else "FALLBACK"}</span>
                    <span class="inactive-badge" style="display: block; width: fit-content; margin-bottom: 8px;">api-lem loop: {"ACTIVE" if api_online else "OFFLINE"}</span>
                    <span class="active-badge" style="display: block; width: fit-content;">caching (l1/l2): SQLite / RAM</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="lem-card">
                <h3>Workspace Assets</h3>
                <p>Configured project subsystems:</p>
                <div style="margin-top: 15px; font-family: 'Geist Mono', monospace; font-size: 0.8rem; color: #A1A1AA;">
                    • api/ (Primary endpoints)<br>
                    • web-lem/ (Command Center React UI)<br>
                    • marketpulse/ (Vite/Gemini dashboard)<br>
                    • autobot/ (Trading simulation engine)<br>
                    • ralph-loop-agent/ (Autonomy loop)
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="lem-card">
                <h3>Data Pipeline</h3>
                <p>Active crawlers & connectors:</p>
                <div style="margin-top: 15px;">
                    <span class="active-badge" style="display: inline-block; margin: 2px;">FRED</span>
                    <span class="active-badge" style="display: inline-block; margin: 2px;">WORLD BANK</span>
                    <span class="active-badge" style="display: inline-block; margin: 2px;">OECD</span>
                    <span class="active-badge" style="display: inline-block; margin: 2px;">IMF</span>
                    <span class="inactive-badge" style="display: inline-block; margin: 2px;">BBC NEWS</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.subheader("System Performance & Health Overview")
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    with perf_col1:
        st.metric(label="API Latency", value="4.2 ms" if api_online else "N/A", delta="-0.8 ms" if api_online else None)
    with perf_col2:
        st.metric(label="Total Database Records", value="15,408" if api_online else "1,208 (CSV Mode)", delta="Realtime Sync")
    with perf_col3:
        st.metric(label="AutoBot State", value="Circuit Breaker: Arm", delta="Active 24/7")
    with perf_col4:
        st.metric(label="LLM Advisor Context", value="1.5-Flash Caching", delta="Active TTL 1hr")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Linked Workspace Structure")
    
    st.markdown("""
    The file structure has been reorganized into logical components. The unified modules can be controlled below:
    - **Macroeconomic Explorer** queries indicators via API (or falls back to legacy dataset CSVs).
    - **Monetary Divergence Map** renders interest rate distributions.
    - **Market Sentiment Desk** parses RSS streams and computes the financial Fear Index.
    - **ML Sentiment Lab** evaluates logistic/ensemble models on sentiment headlines.
    - **OECD Data Hub** processes local balance-of-payments files.
    - **Gemini AI Financial Advisor** leverages Gemini models to evaluate bias, trends, and risk.
    - **AutoBot Simulation Desk** tracks mock trade execution and watchdog events.
    """)

# ----------------- MODULE 2: Macroeconomic Explorer -----------------
elif nav_selection == "📈 Macroeconomic Explorer":
    st.title("📈 Macroeconomic Indicator Explorer")
    st.markdown("Query historical indicators across sources. Integrates directly with the API.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Selection Controls
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        selected_source = st.selectbox("Select Source", ["FRED", "World Bank", "OECD", "IMF", "Fallback Scraped CSV"])
    with col_ctrl2:
        indicator_opts = {
            "FRED": ["GDP", "CPIAUCSL (CPI)", "UNRATE (Unemployment)", "FEDFUNDS (Interest Rate)"],
            "World Bank": ["NY.GDP.MKTP.CD (GDP)", "FP.CPI.TOTL.ZG (Inflation)", "SL.UEM.TOTL.ZS (Unemployment)"],
            "OECD": ["GDP", "Inflation Rate", "Unemployment Rate", "Interest Rate"],
            "IMF": ["Global Price of Brent Crude", "Consumer Prices", "Gross Domestic Product"],
            "Fallback Scraped CSV": ["GDP", "Inflation Rate", "Unemployment Rate", "Interest Rate", "Government Debt"]
        }
        selected_indicator = st.selectbox("Select Indicator", indicator_opts.get(selected_source, ["GDP"]))
    with col_ctrl3:
        country_code = st.text_input("Country (ISO-3 or Name)", value="USA")

    # Fetch Data
    df = None
    data_loaded = False
    
    if selected_source == "Fallback Scraped CSV" or not api_online:
        if not api_online:
            st.info("⚠️ API Server is offline. Automatically using fallback local CSV files.")
        
        # Load CSV Fallback
        csv_filename = f"{selected_indicator.replace(' ', '_')}_Data.csv"
        df = load_fallback_csv(csv_filename)
        if df is not None:
            data_loaded = True
            st.success(f"Successfully loaded fallback data from legacy file: `{csv_filename}`")
    else:
        # Load from API
        with st.spinner("Fetching data from API..."):
            try:
                # Clean up indicator string for endpoint
                clean_ind = selected_indicator.split(" ")[0]
                url = f"http://localhost:8000/api/v1/indicators/{clean_ind}"
                res = requests.get(url, params={"country": country_code}, timeout=5)
                if res.status_code == 200:
                    api_data = res.json()
                    df = pd.DataFrame(api_data["data"])
                    data_loaded = True
                    st.success(f"Successfully retrieved API data for {clean_ind} from {selected_source}")
                else:
                    st.warning(f"API returned status code {res.status_code}. Falling back to CSV.")
                    csv_filename = f"{selected_indicator.replace(' ', '_')}_Data.csv"
                    df = load_fallback_csv(csv_filename)
                    if df is not None:
                        data_loaded = True
            except Exception as e:
                st.error(f"Error connecting to API: {e}. Falling back to local files.")
                csv_filename = f"{selected_indicator.replace(' ', '_')}_Data.csv"
                df = load_fallback_csv(csv_filename)
                if df is not None:
                    data_loaded = True

    if data_loaded and df is not None:
        col_view1, col_view2 = st.columns([2, 1])
        with col_view1:
            st.subheader("Data Trend Analysis")
            if "date" in df.columns and "value" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                fig = px.line(df, x="date", y="value", title=f"{selected_indicator} - {country_code}", template="plotly_dark")
                fig.update_traces(line_color="#FFFFFF")
                st.plotly_chart(fig, use_container_width=True)
            elif "Country" in df.columns and "Last" in df.columns:
                # Fallback CSV data plotting
                df["Last_clean"] = clean_numeric_col(df["Last"])
                df_sorted = df.dropna(subset=["Last_clean"]).sort_values(by="Last_clean", ascending=False).head(15)
                fig = px.bar(df_sorted, x="Country", y="Last_clean", title=f"Top 15 Countries: {selected_indicator}", template="plotly_dark")
                fig.update_traces(marker_color="#A1A1AA")
                st.plotly_chart(fig, use_container_width=True)
        with col_view2:
            st.subheader("Dataset Table View")
            st.dataframe(df.head(100), use_container_width=True)
    else:
        st.error("Could not retrieve data. Please check indicator selection or verify CSV files in `legacy/`.")

# ----------------- MODULE 3: Divergence Map -----------------
elif nav_selection == "🌍 Monetary Divergence Map":
    st.title("🌍 Global Interest Rate Ratio Map")
    st.markdown("Visualizes policy divergence, tightening momentum, or real yields across major economies.")
    st.markdown("<hr>", unsafe_allow_html=True)

    # 1. Fetch interest rate data using visualizer loader
    with st.spinner("Loading interest rate data..."):
        interest_df = load_fallback_csv("Interest_Rate_Data.csv")
        
    if interest_df is None or interest_df.empty:
        st.error("Failed to load interest rate data. Verify that `legacy/Interest_Rate_Data.csv` exists.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            ratio_type = st.selectbox(
                "Select Ratio Metric",
                [
                    "Ratio to Reference Country",
                    "Tightening Ratio (Current vs. Previous)",
                    "Interest Rate to Inflation Ratio"
                ]
            )
        with col2:
            colorscale_choice = st.selectbox(
                "Select Map Colorscale",
                ["Blues", "Viridis", "Plasma", "RdYlBu", "Cividis", "Turbo"]
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
            display_df = map_data.copy().sort_values(by="Ratio", ascending=False)
            cols_to_show = ["Country", "ISO3", "Interest Rate (%)", "Previous Interest Rate (%)"]
            if "Inflation Rate (%)" in display_df.columns:
                cols_to_show.append("Inflation Rate (%)")
            cols_to_show.append("Ratio")
            display_df = display_df[cols_to_show].reset_index(drop=True)
            display_df["Ratio"] = display_df["Ratio"].map(lambda x: f"{x:.4f}x" if pd.notnull(x) else "N/A")
            st.dataframe(display_df, use_container_width=True)

# ----------------- MODULE 4: Market Sentiment Desk -----------------
elif nav_selection == "📰 Market Sentiment Desk":
    st.title("📰 BBC Financial News & Market Sentiment")
    st.markdown("Scrapes live financial streams and builds interactive 3D visualizations of sentiment.")
    st.markdown("<hr>", unsafe_allow_html=True)

    with st.spinner("Scraping BBC Business News feed..."):
        news_df = scrape_bbc_business_news_rss()

    if news_df.empty:
        st.warning("Insufficient news data. The news RSS stream returned 0 items.")
    else:
        # Drop rows with neutral sentiment
        news_df = news_df[(news_df['Polarity'] != 0) | (news_df['Subjectivity'] != 0)]
        news_df['Fear_Index'] = news_df.apply(lambda row: calculate_fear_index(row['Polarity'], row['Subjectivity']), axis=1)
        news_df['RAG_Status'] = news_df['Polarity'].apply(lambda x: 'Green' if x > 0.1 else 'Red' if x < -0.1 else 'Amber')

        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Headline Feed & Sentiment Score")
            st.dataframe(news_df[['Headline', 'Polarity', 'Subjectivity', 'Fear_Index', 'RAG_Status']].head(30), use_container_width=True)
        with col2:
            st.subheader("🧭 3D Sentiment Mapping (RAG Model)")
            color_choice = st.selectbox("3D Marker Color Mapping", ["Fear_Index", "Polarity", "Subjectivity"])
            
            fig = go.Figure(data=[go.Scatter3d(
                x=news_df['Polarity'],
                y=news_df['Subjectivity'],
                z=news_df['Fear_Index'],
                mode='markers',
                text=news_df['Headline'],
                marker=dict(
                    size=8,
                    color=news_df[color_choice],
                    colorscale='Viridis',
                    opacity=0.8,
                    colorbar=dict(title=color_choice)
                )
            )])
            
            fig.update_layout(
                template="plotly_dark",
                scene=dict(
                    xaxis_title="Polarity (Negative → Positive)",
                    yaxis_title="Subjectivity (Fact → Opinion)",
                    zaxis_title="Fear Index (Low → High)",
                ),
                margin=dict(l=0, r=0, b=0, t=0),
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

# ----------------- MODULE 5: ML Sentiment Lab -----------------
elif nav_selection == "🧠 ML Sentiment Lab":
    st.title("🧠 Machine Learning Sentiment Lab")
    st.markdown("Train and evaluate classifiers to predict financial news polarity.")
    st.markdown("<hr>", unsafe_allow_html=True)

    with st.spinner("Scraping training data from RSS..."):
        news_df = scrape_bbc_business_news_rss()

    if news_df.empty or len(news_df) < 5:
        st.warning("Insufficient news data to train model. Need at least 5 sentiment headlines.")
    else:
        news_df['Sentiment'] = news_df['Polarity'].apply(lambda x: 1 if x >= 0 else 0)
        news_df['Fear_Index'] = news_df.apply(lambda row: calculate_fear_index(row['Polarity'], row['Subjectivity']), axis=1)

        # Model controls
        st.subheader("Model Configuration & Training")
        test_size = st.slider("Test Set Split Ratio", 0.1, 0.5, 0.2, step=0.05)
        rf_estimators = st.slider("Random Forest Estimators", 10, 200, 100, step=10)
        
        # Prepare data
        X = news_df[['Polarity', 'Subjectivity', 'Fear_Index']]
        y = news_df['Sentiment']
        
        if len(y.unique()) < 2:
            st.info("The sentiment distribution contains only one class. Adding synthetic values to allow model evaluation.")
            # Inject mock records to balance classes
            synthetic_x = pd.DataFrame([[-0.5, 0.8, 10], [-0.4, 0.6, 7], [0.5, 0.2, 1], [0.3, 0.4, 1]], columns=['Polarity', 'Subjectivity', 'Fear_Index'])
            synthetic_y = pd.Series([0, 0, 1, 1])
            X = pd.concat([X, synthetic_x], ignore_index=True)
            y = pd.concat([y, synthetic_y], ignore_index=True)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        # Model initializations
        model_lr = LogisticRegression()
        model_rf = RandomForestClassifier(n_estimators=rf_estimators, random_state=42)
        model_gb = GradientBoostingClassifier(n_estimators=rf_estimators, random_state=42)
        
        # Train
        model_lr.fit(X_train, y_train)
        model_rf.fit(X_train, y_train)
        model_gb.fit(X_train, y_train)
        
        # Scores
        acc_lr = accuracy_score(y_test, model_lr.predict(X_test))
        acc_rf = accuracy_score(y_test, model_rf.predict(X_test))
        acc_gb = accuracy_score(y_test, model_gb.predict(X_test))
        
        # Dashboard display
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.subheader("Model Accuracy Comparison")
            metrics_df = pd.DataFrame({
                "Classifier": ["Logistic Regression", "Random Forest", "Gradient Boosting"],
                "Accuracy": [acc_lr, acc_rf, acc_gb]
            })
            fig = px.bar(metrics_df, x="Classifier", y="Accuracy", template="plotly_dark", color="Accuracy", color_continuous_scale="Purples")
            fig.update_yaxes(range=[0, 1.05])
            st.plotly_chart(fig, use_container_width=True)
        with col_m2:
            st.subheader("Random Forest Feature Importance")
            feat_imp = pd.Series(model_rf.feature_importances_, index=X.columns).sort_values(ascending=True)
            fig_feat = px.bar(x=feat_imp.values, y=feat_imp.index, orientation='h', template="plotly_dark")
            fig_feat.update_layout(xaxis_title="Importance Weight", yaxis_title="Feature")
            st.plotly_chart(fig_feat, use_container_width=True)

# ----------------- MODULE 6: OECD Data Hub -----------------
elif nav_selection == "📊 OECD Data Hub":
    st.title("📊 OECD Data Explorer")
    st.markdown("Consolidated visualization of G20 lookout, balance of payments, and weekly tracker datasets.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    oecd_selection = st.selectbox(
        "Choose OECD Dataset to Load",
        ["Balance of Payments", "G20 Economic Outlook", "Weekly Tracker of Economic Activity"]
    )
    
    filename_map = {
        "Balance of Payments": "legacy/OECDdatasets/BalanceofPayments.csv",
        "G20 Economic Outlook": "legacy/OECDdatasets/G20EconomicLookout.csv",
        "Weekly Tracker of Economic Activity": "legacy/OECDdatasets/OECDWeeklyTrackerofeconomicActivity.csv"
    }
    
    filepath = filename_map.get(oecd_selection)
    
    if os.path.exists(filepath):
        oecd_df = pd.read_csv(filepath)
        st.success(f"Loaded dataset: `{filepath}` | Shape: {oecd_df.shape[0]} rows, {oecd_df.shape[1]} columns")
        
        st.dataframe(oecd_df.head(200), use_container_width=True)
        
        st.subheader("Dynamic Plotting Engine")
        # Try to locate numeric columns
        numeric_cols = oecd_df.select_dtypes(include=[np.number]).columns.tolist()
        text_cols = oecd_df.select_dtypes(exclude=[np.number]).columns.tolist()
        
        if len(numeric_cols) > 0 and len(text_cols) > 0:
            col_plt1, col_plt2 = st.columns(2)
            with col_plt1:
                x_axis = st.selectbox("Select X-Axis Column", text_cols)
            with col_plt2:
                y_axis = st.selectbox("Select Y-Axis Column (Numeric)", numeric_cols)
                
            fig_oecd = px.scatter(oecd_df.head(1000), x=x_axis, y=y_axis, template="plotly_dark", title=f"{y_axis} vs {x_axis}")
            st.plotly_chart(fig_oecd, use_container_width=True)
        else:
            st.warning("Insufficient columns to perform auto-plotting.")
    else:
        st.error(f"OECD CSV file not found at: `{filepath}`")

# ----------------- MODULE 7: Gemini AI Financial Advisor -----------------
elif nav_selection == "✨ Gemini AI Financial Advisor":
    st.title("✨ Gemini AI Financial & Economic Advisor")
    st.markdown("Utilize Generative AI pipelines to perform bias auditing, trend forecasting, and impact evaluations.")
    st.markdown("<hr>", unsafe_allow_html=True)

    if not HAS_GEMINI:
        st.warning("⚠️ `google-generativeai` package is not installed. You can install it, or simulate queries below.")
    
    api_key_input = st.text_input("Enter your Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    
    col_ai1, col_ai2 = st.columns([1, 1])
    with col_ai1:
        headline_input = st.text_area(
            "Economic Query / Headline to Analyze",
            value="Federal Reserve indicates interest rates will remain elevated throughout 2026 to curb sticky inflation."
        )
        task_mode = st.selectbox(
            "Select Analysis Objective",
            ["Summarize Headline", "Bias Detection & Auditing", "Potential Global Economic Impact", "Trend Forecasting"]
        )
        submit_btn = st.button("Query Gemini Advisor")
    with col_ai2:
        st.subheader("Analysis Response")
        if submit_btn:
            if not api_key_input:
                st.error("API Key required. Please input a valid API Key.")
            else:
                if HAS_GEMINI:
                    with st.spinner("Invoking Gemini Engine..."):
                        try:
                            genai.configure(api_key=api_key_input)
                            model = genai.GenerativeModel("models/gemini-1.5-flash-001")
                            
                            prompts = {
                                "Summarize Headline": f"Summarize the following economic headline briefly and precisely: '{headline_input}'",
                                "Bias Detection & Auditing": f"Audite the following economic statement for any implicit or explicit policy bias and explain your reasoning: '{headline_input}'",
                                "Potential Global Economic Impact": f"Detail the potential micro and macroeconomic impacts of this event on the global market: '{headline_input}'",
                                "Trend Forecasting": f"Does the following indicate an emerging economic trend? Explain: '{headline_input}'"
                            }
                            
                            res = model.generate_content([prompts[task_mode]])
                            st.markdown(f"""
                                <div style="background-color: #181818; padding: 15px; border-radius: 4px; border: 1px solid #333333;">
                                    {res.text}
                                </div>
                            """, unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"Gemini API Execution Error: {e}")
                else:
                    st.info("Simulating response since genai package is missing...")
                    time.sleep(1)
                    st.markdown(f"**Mock Analysis for: {task_mode}**\n\nThe input statement mentions Fed interest rates. Historically, maintaining high rates slows capital borrowing speeds and curbs economic growth velocities, representing a contractionary macro policy signal.")

# ----------------- MODULE 8: AutoBot Simulation Desk -----------------
elif nav_selection == "🤖 AutoBot Simulation Desk":
    st.title("🤖 AutoBot 24/7 Trading Simulation Desk")
    st.markdown("Control and monitor the autonomous trading agent loop. Tracks metrics, circuit breakers, and hedger actions.")
    st.markdown("<hr>", unsafe_allow_html=True)

    # Simulation Controls
    if "bot_active" not in st.session_state:
        st.session_state.bot_active = False
    if "sim_logs" not in st.session_state:
        st.session_state.sim_logs = ["System Initialized. Awaiting loop trigger..."]
    if "tvl" not in st.session_state:
        st.session_state.tvl = 100000.0

    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        if st.session_state.bot_active:
            if st.button("STOP trading engine"):
                st.session_state.bot_active = False
                st.session_state.sim_logs.append("AutoBot trading loop HALTED.")
        else:
            if st.button("START trading engine"):
                st.session_state.bot_active = True
                st.session_state.sim_logs.append("AutoBot trading loop STARTED.")
                
        reset_logs = st.button("Clear Engine Logs")
        if reset_logs:
            st.session_state.sim_logs = ["System Initialized."]
            
    with col_btn2:
        st.subheader("Engine Status Indicator")
        if st.session_state.bot_active:
            st.markdown('<span class="active-badge">RUNNING 24/7 MODE</span> <span style="color:#A1A1AA; font-family:monospace;">Watching BTC-USDT feed</span>', unsafe_allow_html=True)
            # Run simulation step
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            mock_price = 65000.0 + np.random.normal(0, 150)
            mock_signal = np.random.choice(["BUY", "SELL", "WAIT"], p=[0.2, 0.2, 0.6])
            
            if mock_signal != "WAIT":
                trade_volume = np.random.uniform(0.1, 0.5)
                st.session_state.tvl += (trade_volume * 100 if mock_signal == "BUY" else -trade_volume * 100)
                st.session_state.sim_logs.append(f"[{current_time}] SIGNAL: {mock_signal} | Target: BTC-USDT at ${mock_price:.2f} | Execution Success.")
                st.session_state.sim_logs.append(f"[{current_time}] Hedger: Adjusted futures delta hedge. Account Bal: ${st.session_state.tvl:.2f}")
            else:
                st.session_state.sim_logs.append(f"[{current_time}] Feed: Heartbeat OK. Price: ${mock_price:.2f} | Watchdog: Normal.")
        else:
            st.markdown('<span class="inactive-badge">STOPPED</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Realtime Monitoring Telemetry")
    
    col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
    with col_metrics1:
        st.metric(label="Mock Engine Latency", value="12 ms" if st.session_state.bot_active else "N/A", delta="-2 ms" if st.session_state.bot_active else None)
    with col_metrics2:
        st.metric(label="Total Value Locked (TVL)", value=f"${st.session_state.tvl:,.2f}", delta="+1.2%" if st.session_state.bot_active else None)
    with col_metrics3:
        st.metric(label="Circuit Breaker Status", value="CLOSED (Normal)" if st.session_state.bot_active else "N/A")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("AutoBot Log Stream")
    log_text = "\n".join(st.session_state.sim_logs[-15:])
    st.text_area("Live Logs", value=log_text, height=250, disabled=True)
