import plotly.express as px
import streamlit as st

def visualize_polarity_distribution(news_df):
    fig = px.histogram(news_df, x='Polarity', nbins=20, title='Sentiment Polarity Distribution', template='plotly_dark')
    st.plotly_chart(fig)

def visualize_rag_status_distribution(news_df):
    fig = px.histogram(news_df, x='RAG_Status', color='RAG_Status', title='RAG Status Distribution', template='plotly_dark')
    st.plotly_chart(fig)

def visualize_fear_index_distribution(news_df):
    fig = px.histogram(news_df, x='Fear_Index', nbins=10, title='Fear Index Distribution', template='plotly_dark')
    st.plotly_chart(fig)
