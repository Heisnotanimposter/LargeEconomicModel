# -*- coding: utf-8 -*-
"""GeminiFinancialDecisionSupport

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/#fileId=https%3A//storage.googleapis.com/kaggle-colab-exported-notebooks/geminifinancialdecisionsupport-8f6b5116-8e0b-4ab9-ad1c-cd5cc2de5d2c.ipynb%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com/20241128/auto/storage/goog4_request%26X-Goog-Date%3D20241128T033327Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D6aa30a3896563a0dea0fb52ccc31921cef29c607725a50f6b9c8b32412c04f5407c154a843cbdf14e70631e51f9f7a4dce08b4961bc353a05c68c6209f0821166fc37ba220e14653f1d4eb436b831ca5f5e96b39f0f40edf96ec944659b846aa98637df30621bcfbce71965ce23c52080cfe1b888b637d5dd4572ff64037a7e9b111a96dcf97228943597db7840a34a67d9a02fe10163ec2e36f1b9823c1b2ea28241ba2e171adf8bf03f3562c6bfb8598f87177b335c5157f553d8e897cfb497d36c0598f2c65d43a5ba3f0448840f96647ba3536db78c7184159156d3eee09b0b8a9ccde20196c23d2be28b01280b83c92352690249179df495403b1e84f42
"""

# IMPORTANT: SOME KAGGLE DATA SOURCES ARE PRIVATE
# RUN THIS CELL IN ORDER TO IMPORT YOUR KAGGLE DATA SOURCES.
import kagglehub
kagglehub.login()

# IMPORTANT: RUN THIS CELL IN ORDER TO IMPORT YOUR KAGGLE DATA SOURCES,
# THEN FEEL FREE TO DELETE THIS CELL.
# NOTE: THIS NOTEBOOK ENVIRONMENT DIFFERS FROM KAGGLE'S PYTHON
# ENVIRONMENT SO THERE MAY BE MISSING LIBRARIES USED BY YOUR
# NOTEBOOK.

gemini_long_context_path = kagglehub.competition_download('gemini-long-context')

print('Data source import complete.')

"""# Project Initialization
## Purpose:
- Import essential libraries for fetching and parsing financial data, making API calls, and visualizing outputs.

## Role in Project:
- Provides the foundation for all subsequent functionality, ensuring smooth data processing and interaction with the Gemini API.
"""

!pip install feedparser
!pip install google-generativeai
import requests
from bs4 import BeautifulSoup
import pandas as pd
import feedparser
import json
import time
from collections import Counter, defaultdict
import matplotlib.pyplot as plt

print("Libraries successfully imported.")

"""# Gemini API Setup
## Purpose:
- Authenticate and initialize the Gemini API for long-context processing.

## Role in Project:
- Sets up the central AI model for analysis, leveraging its unique capabilities for large-context handling.
"""

# Import the library
import google.generativeai as genai

# Initialize the secrets client
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()

# Fetch secrets
api_key = user_secrets.get_secret("GEMINI")  # Gemini API Key

# Configure the generative AI client
genai.configure(api_key=api_key)

# Set up and verify the model
model_name = "models/gemini-1.5-flash"  # Include the correct prefix
gemini_model = genai.get_model(name=model_name)

# Validate the model initialization
if gemini_model:
    print(f"Model '{model_name}' initialized successfully!")
else:
    raise ValueError(f"Failed to initialize model '{model_name}'. Check your configuration and API key.")

"""# Fetching News Headlines
## Purpose:
- Retrieve real-time news headlines for analysis.

## Role in Project:
- Serves as input data for testing Gemini’s long-context capabilities dynamically.
"""

def fetch_news_headlines(rss_url="https://feeds.bbci.co.uk/news/world/rss.xml", max_headlines=5):
    """Fetches the latest news headlines."""
    feed = feedparser.parse(rss_url)
    return [entry.title for entry in feed.entries[:max_headlines]]

# Fetch headlines
news_headlines = fetch_news_headlines()
print("Fetched headlines:")
for idx, headline in enumerate(news_headlines, 1):
    print(f"{idx}. {headline}")

"""# Query Logging
## Purpose:
- Log queries, responses, and metadata for tracking performance.

## Role in Project:
- Enables detailed analysis of the Gemini model’s behavior and efficiency.
"""

log_data = []

def log_query(query, response=None, success=True, tokens=0, error_message=None):
    """Logs queries and their associated metadata."""
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "response": response,
        "success": success,
        "tokens": tokens,
        "error_message": error_message,
    }
    log_data.append(log_entry)
    print(f"Logged query: {query} | Success: {success}")

"""# Log Analysis
## Purpose:
- Analyze logged queries to compute metrics like success rate, error rate, and token usage.

## Role in Project:
- Provides insights for improving model efficiency and aligning with competition metrics.
"""

def analyze_logs():
    """Analyzes logged data and computes metrics."""
    metrics = {
        "total_queries": len(log_data),
        "successful_queries": sum(1 for log in log_data if log["success"]),
        "error_queries": sum(1 for log in log_data if not log["success"]),
        "total_tokens_used": sum(log.get("tokens", 0) for log in log_data),
    }
    errors = Counter(log["error_message"] for log in log_data if not log["success"])
    return metrics, errors

metrics, error_types = analyze_logs()
print(metrics)
print("Error Types:", error_types)

"""# Query Caching
## Purpose:
- Cache query results to minimize redundant API calls.

## Role in Project:
- Demonstrates efficient handling of repetitive queries, leveraging Gemini’s long-context capabilities.
"""

cache = defaultdict(lambda: None)

def cached_query(query, model):
    """Fetches results from cache or executes the query."""
    if query in cache:
        print("Cache hit:", query)
        return cache[query]
    response = model.generate_content(query)
    cache[query] = response
    return response

"""# Query Batching
## Purpose:
- Group and execute queries in batches for efficiency.

## Role in Project:
- Reduces the number of API calls, demonstrating best practices for large-context processing.
"""

def batch_queries(queries, model, batch_size=5):
    """Processes queries in batches."""
    results = []
    for i in range(0, len(queries), batch_size):
        batch = queries[i:i + batch_size]
        print(f"Processing batch: {batch}")
        results.extend([cached_query(q, model) for q in batch])
    return results

"""# Batch Execution with Retry Logic
## Purpose:
- Handle errors during batch execution by retrying failed queries.

## Role in Project:
- Ensures robust query handling, improving reliability.
"""

def execute_with_retries(queries, model, max_retries=3):
    """Executes queries with retry logic."""
    results = []
    for query in queries:
        retries = 0
        while retries < max_retries:
            try:
                results.append(cached_query(query, model))
                break
            except Exception as e:
                print(f"Error: {e} | Retrying... ({retries + 1}/{max_retries})")
                retries += 1
    return results

"""# Real-Time Headline Analysis
## Purpose:
- Analyze real-time headlines using the batching and caching approach.

## Role in Project:
- Demonstrates practical use of Gemini’s long-context window for compelling insights.
"""

# Example usage
queries = [f"Summarize: {headline}" for headline in news_headlines]
results = batch_queries(queries, gemini_model)
for result in results:
    print(result)

"""# Advanced Query Analysis
## Purpose:
- Evaluate success and error counts across query types.

## Role in Project:
- Provides deeper insights into the model’s performance across different tasks.
"""

def analyze_query_types(log_data):
    """Counts successes and errors by query type."""
    type_success = Counter()
    type_error = Counter()

    for log in log_data:
        query_type = log["query"].split(":")[0]  # Extract type
        if log["success"]:
            type_success[query_type] += 1
        else:
            type_error[query_type] += 1

    return type_success, type_error

type_success, type_error = analyze_query_types(log_data)

# Visualization
query_types = list(type_success.keys())
success_counts = [type_success[t] for t in query_types]
error_counts = [type_error[t] for t in query_types]

plt.bar(query_types, success_counts, label="Success", alpha=0.7)
plt.bar(query_types, error_counts, label="Error", alpha=0.7, bottom=success_counts)
plt.xlabel("Query Types")
plt.ylabel("Counts")
plt.title("Query Success vs Error by Type")
plt.legend()
plt.show()

"""# Token Usage Distribution
## Purpose:
- Examine token usage across queries.

## Role in Project:
- Highlights how efficiently the Gemini model uses its long context window.
"""

def plot_token_usage(log_data):
    """Plots token usage distribution."""
    tokens_used = [log["tokens"] for log in log_data if log["success"]]

    plt.hist(tokens_used, bins=10, edgecolor="black")
    plt.xlabel("Tokens Used")
    plt.ylabel("Frequency")
    plt.title("Token Usage Distribution")
    plt.show()

plot_token_usage(log_data)

"""# Scenario-Specific Application
## Purpose:
- Use the Gemini model to analyze real-time economic scenarios.

## Role in Project:
- Showcases the application of Gemini’s long context window for strategic decision-making.
"""

# Example scenario: Analyze economic trends
scenario_query = (
    "Analyze the potential economic impact of current interest rate hikes by central banks "
    "on global markets, considering recent inflation trends."
)

scenario_result = gemini_model.generate_content(scenario_query)
print("Scenario Analysis Result:", scenario_result.text)

"""# Performance Summary Dashboard
## Purpose:
- Consolidate all performance metrics into a visual summary.

## Role in Project:
- Provides a clear and concise overview of the project’s outcomes.
"""

from matplotlib.gridspec import GridSpec

def performance_dashboard(log_data):
    """Displays a dashboard of key metrics."""
    metrics, error_types = analyze_logs()
    fig = plt.figure(figsize=(12, 6))
    gs = GridSpec(2, 3, figure=fig)

    # Success vs Error
    ax1 = fig.add_subplot(gs[0, 0])
    labels = ["Success", "Error"]
    sizes = [metrics["successful_queries"], metrics["error_queries"]]
    ax1.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax1.set_title("Query Success Rate")

    # Token Usage Histogram
    ax2 = fig.add_subplot(gs[0, 1])
    tokens_used = [log["tokens"] for log in log_data if log["success"]]
    ax2.hist(tokens_used, bins=10, edgecolor="black")
    ax2.set_title("Token Usage Distribution")
    ax2.set_xlabel("Tokens Used")
    ax2.set_ylabel("Frequency")

    # Error Types
    ax3 = fig.add_subplot(gs[0, 2])
    error_labels = list(error_types.keys())
    error_counts = list(error_types.values())
    ax3.barh(error_labels, error_counts, color="salmon")
    ax3.set_title("Error Types")
    ax3.set_xlabel("Counts")

    # Display
    plt.tight_layout()
    plt.show()

performance_dashboard(log_data)

# Function to batch process queries
def batch_process_queries(model, batched_queries, batch_size=5):
    batched_results = []
    for i in range(0, len(batched_queries), batch_size):
        batch = batched_queries[i:i + batch_size]
        try:
            responses = model.generate_content(batch)
            batched_results.extend(responses)
            print(f"Processed batch {i // batch_size + 1}: {batch}")
        except Exception as e:
            print(f"Error processing batch {i // batch_size + 1}: {e}")
            batched_results.extend([None] * len(batch))
    return batched_results

# Example batched queries
batched_queries = [
    f"Analyze headline: '{headline}'" for headline in headlines
]
batched_results = batch_process_queries(gemini_model, batched_queries)

"""#### Purpose:
- Implements batch processing for grouped queries to reduce the number of API calls.

#### Role in Project:
- Enhances efficiency by leveraging grouped operations.
- Aligns with best practices for API usage, especially with a large context window.
"""

# Sample log data for visualization
log_data = [
    {"query": "Query 1", "tokens": 120},
    {"query": "Query 2", "tokens": 250},
    {"query": "Query 3", "tokens": 180},
    {"query": "Query 4", "tokens": 310},
    {"query": "Query 5", "tokens": 90},
]

# Function to visualize token usage
def visualize_token_usage(log_data):
    queries = [log["query"] for log in log_data]
    tokens = [log["tokens"] for log in log_data]

    plt.figure(figsize=(10, 6))
    plt.bar(queries, tokens, color='skyblue')
    plt.xlabel("Queries")
    plt.ylabel("Tokens Used")
    plt.title("Token Usage Across Queries")
    plt.show()

# Generate visualization
visualize_token_usage(log_data)

"""#### Purpose:
- Visualizes token usage across multiple queries using a bar chart.

#### Role in Project:
- Provides clear insights into token distribution for performance monitoring.
- Highlights queries that consume the most tokens, helping optimize usage.
"""

# Function to analyze errors and retry failed queries
def analyze_and_retry_errors(log_data, max_retries=3):
    error_stats = {}
    retried_queries = []

    for log in log_data:
        if not log.get("success"):
            error_message = log.get("error_message", "Unknown Error")
            error_stats[error_message] = error_stats.get(error_message, 0) + 1

            # Retry logic
            retries = 0
            while retries < max_retries:
                try:
                    print(f"Retrying query: {log['query']}")
                    response = gemini_model.generate_content([log['query']])[0]
                    retried_queries.append({"query": log["query"], "response": response.text, "success": True})
                    print(f"Retry successful for query: {log['query']}")
                    break
                except Exception as e:
                    retries += 1
                    print(f"Retry {retries}/{max_retries} failed for query: {log['query']}")
                    if retries == max_retries:
                        print(f"Max retries reached for query: {log['query']}")

    return error_stats, retried_queries

# Example error log
log_data_with_errors = [
    {"query": "Summarize the following headline: 'Market volatility spikes amid global uncertainty.'", "success": False, "error_message": "429 Resource has been exhausted."},
    {"query": "Analyze headline impact: 'Tech stocks rally after positive earnings reports.'", "success": False, "error_message": "Timeout error."},
]

# Perform error analysis and retry
error_stats, retried_queries = analyze_and_retry_errors(log_data_with_errors)
print("Error Statistics:", error_stats)
print("Retried Queries:", retried_queries)

"""#### Purpose:
- Implements granular error categorization and retry logic for failed queries.

#### Role in Project:
- Enhances robustness by identifying and addressing common error types.
- Improves the success rate of queries through automated retries.
"""