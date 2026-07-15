# visualizer.py
import os
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

def plot_3d_rag_model(news_df, default_color):
    # Interactive sliders and dropdowns
    point_size = st.sidebar.slider('Point Size', 10, 200, 50)
    color_map = st.sidebar.selectbox('Color Map', ['Reds', 'Greens', 'Blues', 'Viridis', 'Cividis', 'Plasma'])
    elevation = st.sidebar.slider('Elevation Angle', 0, 180, 30)
    axis_azimuth = st.sidebar.slider('Azimuth Angle', 0, 360, 30)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Map RAG status to colors with the chosen color scheme
    rag_color_map = {'Red': 'r', 'Amber': 'orange', 'Green': 'g'}
    colors = news_df['RAG_Status'].map(rag_color_map).tolist()

    # Scatter plot with user-controlled point size
    sc = ax.scatter(
        news_df['Polarity'], news_df['Subjectivity'], news_df['Fear_Index'],
        c=news_df['Fear_Index'], cmap=color_map, s=point_size, alpha=0.8
    )

    # Set axis labels and angles based on user input
    ax.set_xlabel('Polarity')
    ax.set_ylabel('Subjectivity')
    ax.set_zlabel('Fear Index')
    ax.view_init(elev=elevation, azim=axis_azimuth)
    ax.set_title('3D Visualization of RAG Model with Fear Index')

    # Color bar for better visualization
    fig.colorbar(sc, ax=ax, shrink=0.5, aspect=5)
    
    st.pyplot(fig)

# --- World Map with Interest Rate Ratio Implementation ---

COUNTRY_TO_ISO = {
    "switzerland": "CHE",
    "japan": "JPN",
    "singapore": "SGP",
    "canada": "CAN",
    "south korea": "KOR",
    "korea, south": "KOR",
    "china": "CHN",
    "australia": "AUS",
    "united kingdom": "GBR",
    "uk": "GBR",
    "united states": "USA",
    "us": "USA",
    "usa": "USA",
    "saudi arabia": "SAU",
    "indonesia": "IDN",
    "india": "IND",
    "south africa": "ZAF",
    "mexico": "MEX",
    "brazil": "BRA",
    "russia": "RUS",
    "argentina": "ARG",
    "turkey": "TUR",
    "france": "FRA",
    "germany": "DEU",
    "italy": "ITA",
    "spain": "ESP",
    "netherlands": "NLD",
    "belgium": "BEL",
    "austria": "AUT",
    "sweden": "SWE",
    "norway": "NOR",
    "denmark": "DNK",
    "finland": "FIN",
    "poland": "POL",
    "ireland": "IRL",
    "portugal": "PRT",
    "greece": "GRC",
    "new zealand": "NZL",
    "chile": "CHL",
    "colombia": "COL",
    "israel": "ISR",
    "malaysia": "MYS",
    "thailand": "THA",
    "philippines": "PHL",
    "vietnam": "VNM",
}

EUROZONE_ISOS = ["DEU", "FRA", "ITA", "ESP", "NLD", "BEL", "AUT", "PRT", "GRC", "IRL", "FIN", "SVK", "SVN", "EST", "LVA", "LTU", "HRV", "CYP", "MLT"]

ISO_TO_NAME = {
    "CHE": "Switzerland",
    "JPN": "Japan",
    "SGP": "Singapore",
    "CAN": "Canada",
    "KOR": "South Korea",
    "CHN": "China",
    "AUS": "Australia",
    "GBR": "United Kingdom",
    "USA": "United States",
    "SAU": "Saudi Arabia",
    "IDN": "Indonesia",
    "IND": "India",
    "ZAF": "South Africa",
    "MEX": "Mexico",
    "BRA": "Brazil",
    "RUS": "Russia",
    "ARG": "Argentina",
    "TUR": "Turkey",
    "FRA": "France",
    "DEU": "Germany",
    "ITA": "Italy",
    "ESP": "Spain",
    "NLD": "Netherlands",
    "BEL": "Belgium",
    "AUT": "Austria",
    "SWE": "Sweden",
    "NOR": "Norway",
    "DNK": "Denmark",
    "FIN": "Finland",
    "POL": "Poland",
    "IRL": "Ireland",
    "PRT": "Portugal",
    "GRC": "Greece",
    "NZL": "New Zealand",
    "CHL": "Chile",
    "COL": "Colombia",
    "ISR": "Israel",
    "MYS": "Malaysia",
    "THA": "Thailand",
    "PHL": "Philippines",
    "VNM": "Vietnam"
}

def load_fallback_csv(filename):
    possible_paths = [
        filename,
        os.path.join(os.path.dirname(__file__), filename),
        os.path.join("/Users/seungwonlee/LargeEconomicModel", filename)
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                return pd.read_csv(p)
            except Exception:
                pass
    return None

def clean_numeric_col(series):
    if series is None:
        return np.nan
    return pd.to_numeric(
        series.astype(str)
        .str.replace(',', '', regex=False)
        .str.replace('$', '', regex=False)
        .str.replace('%', '', regex=False)
        .str.strip(),
        errors='coerce'
    )

def map_and_expand_countries(df):
    rows = []
    for idx, row in df.iterrows():
        country_name = str(row["Country"]).strip().lower()
        if "euro area" in country_name or "eurozone" in country_name:
            for iso in EUROZONE_ISOS:
                new_row = row.copy()
                new_row["ISO3"] = iso
                new_row["Country"] = f"{ISO_TO_NAME.get(iso, iso)} (Euro Area)"
                rows.append(new_row)
        else:
            iso = COUNTRY_TO_ISO.get(country_name)
            if iso:
                new_row = row.copy()
                new_row["ISO3"] = iso
                new_row["Country"] = ISO_TO_NAME.get(iso, row["Country"])
                rows.append(new_row)
            else:
                new_row = row.copy()
                new_row["ISO3"] = None
                rows.append(new_row)
    return pd.DataFrame(rows)

def plot_world_map_interest_ratio(interest_df, inflation_df, ratio_type, reference_country=None, colorscale="Viridis"):
    """
    Computes interest rate ratio based on ratio_type and plots a world map using Plotly choropleth.
    """
    # 1. Clean and align data
    interest_df = interest_df.copy()
    interest_df["Last"] = clean_numeric_col(interest_df["Last"])
    interest_df["Previous"] = clean_numeric_col(interest_df["Previous"])
    
    # Map country names to ISO-3 codes, expanding Euro Area to its member countries
    interest_mapped = map_and_expand_countries(interest_df)
    interest_mapped = interest_mapped.dropna(subset=["ISO3", "Last"])
    
    # Deduplicate in case of multiple listings for the same ISO-3
    interest_mapped = interest_mapped.sort_values(by="Last", ascending=False).drop_duplicates(subset=["ISO3"])
    
    if ratio_type == "Interest Rate to Inflation Ratio" and inflation_df is not None:
        inflation_df = inflation_df.copy()
        inflation_df["Last"] = clean_numeric_col(inflation_df["Last"])
        inflation_mapped = map_and_expand_countries(inflation_df)
        inflation_mapped = inflation_mapped.dropna(subset=["ISO3", "Last"])
        inflation_mapped = inflation_mapped.sort_values(by="Last", ascending=False).drop_duplicates(subset=["ISO3"])
        
        # Merge datasets on ISO3
        merged = pd.merge(
            interest_mapped,
            inflation_mapped[["ISO3", "Last", "Country"]],
            on="ISO3",
            suffixes=("_interest", "_inflation")
        )
        
        # Compute Ratio: Interest Rate Last / Inflation Rate Last
        # Avoid divide by zero
        merged["Ratio"] = merged["Last_interest"] / merged["Last_inflation"]
        merged.loc[merged["Last_inflation"] == 0, "Ratio"] = np.nan
        
        # Format variables for visualization
        merged["Interest Rate (%)"] = merged["Last_interest"]
        merged["Previous Interest Rate (%)"] = merged["Previous"]
        merged["Inflation Rate (%)"] = merged["Last_inflation"]
        merged["Country"] = merged["Country_interest"]
        
        map_df = merged
        title_text = "Interest Rate to Inflation Ratio (Real Yield Indicator)"
        hover_cols = {
            "ISO3": False,
            "Interest Rate (%)": ":.2f",
            "Inflation Rate (%)": ":.2f",
            "Ratio": ":.4f"
        }
        
    elif ratio_type == "Tightening Ratio (Current vs. Previous)":
        # Compute Ratio: Last / Previous
        map_df = interest_mapped.copy()
        map_df["Ratio"] = map_df["Last"] / map_df["Previous"]
        map_df.loc[map_df["Previous"] == 0, "Ratio"] = np.nan
        
        map_df["Interest Rate (%)"] = map_df["Last"]
        map_df["Previous Interest Rate (%)"] = map_df["Previous"]
        
        title_text = "Monetary Policy Tightening Ratio (Current Rate / Previous Rate)"
        hover_cols = {
            "ISO3": False,
            "Interest Rate (%)": ":.2f",
            "Previous Interest Rate (%)": ":.2f",
            "Ratio": ":.4f"
        }
        
    else:  # Ratio to Reference Country
        if not reference_country:
            reference_country = "USA"
            
        map_df = interest_mapped.copy()
        
        # Find reference rate
        ref_row = map_df[map_df["ISO3"] == reference_country]
        if ref_row.empty:
            # Try by matching text in Country
            ref_row = map_df[map_df["Country"].str.lower().str.contains(reference_country.lower(), na=False)]
            
        if not ref_row.empty:
            ref_rate = ref_row.iloc[0]["Last"]
            ref_name = ref_row.iloc[0]["Country"]
        else:
            ref_rate = 1.0
            ref_name = reference_country
            st.warning(f"Could not find reference country {reference_country} in the dataset. Defaulting to divisor 1.0.")
            
        # Compute Ratio: Last / Reference Last
        if ref_rate != 0:
            map_df["Ratio"] = map_df["Last"] / ref_rate
        else:
            map_df["Ratio"] = np.nan
            
        map_df["Interest Rate (%)"] = map_df["Last"]
        map_df["Previous Interest Rate (%)"] = map_df["Previous"]
        
        title_text = f"Interest Rate Ratio Relative to {ref_name} (Current Country Rate / {ref_rate:.2f}%)"
        hover_cols = {
            "ISO3": False,
            "Interest Rate (%)": ":.2f",
            "Ratio": ":.4f"
        }
        
    # Clean map dataframe
    map_df = map_df.dropna(subset=["Ratio"])
    
    if map_df.empty:
        st.info("No data available to display on the map for the selected configuration.")
        return None
        
    # Plotly Choropleth
    fig = px.choropleth(
        map_df,
        locations="ISO3",
        color="Ratio",
        hover_name="Country",
        hover_data=hover_cols,
        color_continuous_scale=colorscale,
        projection="natural earth",
        title=f"🌐 {title_text}"
    )
    
    # Customizing the appearance
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth',
            lakecolor='rgba(0,0,0,0)',
            landcolor='rgba(220, 220, 220, 0.1)',
            bgcolor='rgba(0,0,0,0)'
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar=dict(
            title="Ratio",
            thicknessmode="pixels", thickness=15,
            lenmode="fraction", len=0.6,
            yanchor="middle", y=0.5,
            ticks="outside"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    return map_df