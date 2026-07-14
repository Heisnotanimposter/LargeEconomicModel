# -*- coding: utf-8 -*-
"""
Refined Notebook: BBC News Analysis with GEMINI API
"""

# Imports
import os
import yaml
import feedparser
import pandas as pd
import pytz
from datetime import datetime, timedelta
from textblob import TextBlob
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import google.generativeai as genai
from kaggle_secrets import UserSecretsClient
import time


# Caching Implementation
class SimpleCache:
    """
    A simple in-memory cache with expiration.
    """
    def __init__(self, expiration_seconds=3600):
        self.cache = {}
        self.expiration_seconds = expiration_seconds

    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if (datetime.now() - timestamp).total_seconds() < self.expiration_seconds:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = (value, datetime.now())


# GEMINI API Configuration
def configure_gemini_api():
    """
    Configures the GEMINI API client.
    """
    user_secrets = UserSecretsClient()
    gemini_api_key = user_secrets.get_secret("GEMINI")
    if not gemini_api_key:
        raise ValueError("GEMINI API Key not found in Kaggle Secrets.")
    genai.configure(api_key=gemini_api_key)
    print("GEMINI API configured successfully!")


# BBC News Data Collection
def fetch_bbc_headlines(category='world'):
    rss_url = f'http://feeds.bbci.co.uk/news/{category}/rss.xml'
    feed = feedparser.parse(rss_url)
    return feed.entries


def filter_headlines_by_time(entries, start_time, end_time):
    filtered_entries = []
    for entry in entries:
        published_time = datetime(*entry.published_parsed[:6], tzinfo=pytz.UTC).astimezone(pytz.timezone('Europe/London'))
        if start_time <= published_time <= end_time:
            filtered_entries.append({
                'title': entry.title,
                'link': entry.link,
                'published': published_time.isoformat(),
                'category': entry.get('category', 'General')
            })
    return filtered_entries


def save_headlines_to_yaml(headlines, filename='bbc_headlines.yaml'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            existing_data = yaml.safe_load(file) or []
    else:
        existing_data = []

    # Combine and deduplicate
    seen_titles = set()
    combined_data = existing_data + headlines
    unique_data = [item for item in combined_data if item['title'] not in seen_titles and not seen_titles.add(item['title'])]

    with open(filename, 'w') as file:
        yaml.dump(unique_data, file, sort_keys=False)


def fetch_and_store_headlines(categories):
    now_uk = datetime.now(pytz.timezone('Europe/London'))
    start_time = now_uk.replace(hour=0, minute=0, second=0, microsecond=0)
    all_headlines = []
    for category in categories:
        entries = fetch_bbc_headlines(category)
        filtered_entries = filter_headlines_by_time(entries, start_time, now_uk)
        all_headlines.extend(filtered_entries)
    save_headlines_to_yaml(all_headlines)


# Sentiment Analysis
def compute_sentiment(headlines):
    sentiment_data = []
    for item in headlines:
        headline = item['title']
        blob = TextBlob(headline)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        rag_status = 'Green' if polarity > 0.1 else 'Amber' if -0.1 <= polarity <= 0.1 else 'Red'
        emoji = '😊' if rag_status == 'Green' else '😐' if rag_status == 'Amber' else '😞'
        sentiment_data.append({
            'Title': headline,
            'Link': item['link'],
            'Published': item['published'],
            'Category': item['category'],
            'Polarity': polarity,
            'Subjectivity': subjectivity,
            'RAG_Status': rag_status,
            'Emoji': emoji
        })
    return pd.DataFrame(sentiment_data)


def save_sentiment_to_yaml(sentiment_df, filename='sentiment_headlines.yaml'):
    data = sentiment_df.to_dict(orient='records')
    with open(filename, 'w') as file:
        yaml.dump(data, file, sort_keys=False)


# GEMINI Summarization
def summarize_headlines(data):
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-001")
    cache = SimpleCache()
    summaries = []
    for item in data:
        headline = item['Title']
        query = f"Summarize the following headline briefly: '{headline}'"

        cached_summary = cache.get(query)
        if cached_summary:
            summary = cached_summary
        else:
            retries, max_retries, backoff = 0, 3, 2
            while retries < max_retries:
                try:
                    response = model.generate_content([query])
                    summary = response.text
                    cache.set(query, summary)
                    break
                except Exception as e:
                    retries += 1
                    time.sleep(backoff ** retries)
                    if retries == max_retries:
                        summary = "Error: Unable to summarize"
        summaries.append({'Title': headline, 'Summary': summary})
    return summaries


def save_summaries_to_yaml(summaries, filename='summarized_headlines.yaml'):
    with open(filename, 'w') as file:
        yaml.dump(summaries, file, sort_keys=False)


# Visualization
def create_category_chart(df):
    category_counts = df['Category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    return px.bar(category_counts, x='Category', y='Count', title='Headlines per Category')


def create_rag_status_pie_chart(df):
    rag_counts = df['RAG_Status'].value_counts().reset_index()
    rag_counts.columns = ['RAG_Status', 'Count']
    return px.pie(rag_counts, names='RAG_Status', values='Count', title='RAG Status Distribution')


def run_dashboard(df):
    app = Dash(__name__)
    app.layout = html.Div(children=[
        html.H1("BBC News Sentiment Dashboard"),
        dcc.Graph(figure=create_category_chart(df)),
        dcc.Graph(figure=create_rag_status_pie_chart(df)),
    ])
    app.run_server(debug=True)


# Execution
if __name__ == "__main__":
    configure_gemini_api()
    categories = ['world', 'business', 'technology', 'health', 'entertainment_and_arts', 'science_and_environment']
    fetch_and_store_headlines(categories)
    headlines = load_sentiment_data('bbc_headlines.yaml')
    sentiment_df = compute_sentiment(headlines)
    save_sentiment_to_yaml(sentiment_df)
    summaries = summarize_headlines(sentiment_df.to_dict(orient='records'))
    save_summaries_to_yaml(summaries)
    run_dashboard(sentiment_df)