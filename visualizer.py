# visualizer.py
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st
from mpl_toolkits.mplot3d import Axes3D

def plot_3d_rag_model(news_df, default_color):
    # Interactive sliders and dropdowns
    point_size = st.sidebar.slider('Point Size', 10, 200, 50)
    color_map = st.sidebar.selectbox('Color Map', ['Reds', 'Greens', 'Blues', 'Viridis', 'Cividis', 'Plasma'])
    elevation = st.sidebar.slider('Elevation Angle', 0, 180, 30)
    azimuth = st.sidebar.slider('Azimuth Angle', 0, 360, 30)
    
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
    ax.view_init(elev=elevation, azim=azimuth)
    ax.set_title('3D Visualization of RAG Model with Fear Index')

    # Color bar for better visualization
    fig.colorbar(sc, ax=ax, shrink=0.5, aspect=5)
    
    st.pyplot(fig)