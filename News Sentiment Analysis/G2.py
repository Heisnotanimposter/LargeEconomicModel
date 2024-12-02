# -*- coding: utf-8 -*-
"""notebookdc56e38780

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/#fileId=https%3A//storage.googleapis.com/kaggle-colab-exported-notebooks/notebookdc56e38780-a9ca0b3a-9503-4613-b10d-c18fded36af4.ipynb%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com/20241128/auto/storage/goog4_request%26X-Goog-Date%3D20241128T062709Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D7186c4f0e89abd16f100112be0a37cb2cb712441ce1f6401985b15a907efaa31329167b0174266fce43f2d2093076382c17665de10dbccf49a65ef62cdca8b0b739c9dd1752c548e71746be86092da8f9ba11634fd3f4dc8a4a22dcac0cc419bb85267a42e0fad84b998cf54bb85357000cd8ad5bf12968a24511f1688906c31a91ed51b3630789da581bc866f06fbf83532c39a99d7066188c207a9042258787abb02a94107c7e31e69d184c8c8fee4c6baada498b3010aa9c05cd27678f47450286a4712bdfe8f14039038607ac80cbd30bd3aa2d280c8cb5263967cf365dd2f08eab809f93445c7ee85cd895aae3bd162523547a7e77a554fe233a7b7629a
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

# -*- coding: utf-8 -*-
"""enhanced_geminiflashfinancialdecisionsupport.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15OIM9PenoOXg8NdZsRppXROEYdwXRTno
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_economic_data(url):
    """
    Fetches economic data from TradingEconomics and returns a DataFrame with enhanced error handling.
    """
    retries = 3
    for attempt in range(retries):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')

            if table is None:
                print(f"Failed to find the table on {url}")
                return None

            headers = [header.get_text(strip=True) for header in table.find_all('th')]
            rows = []
            for row in table.find_all('tr')[1:]:
                columns = row.find_all('td')
                row_data = [column.get_text(strip=True) for column in columns]
                if row_data:
                    rows.append(row_data)

            if not rows:
                print(f"No data found in the table on {url}")
                return None

            df = pd.DataFrame(rows, columns=headers)
            return df
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: Error fetching data from {url} - {e}")
            if attempt == retries - 1:
                print("All retries failed.")
                return None

# Test fetching data
urls = {
    "GDP": "https://tradingeconomics.com/country-list/gdp",
    "Inflation Rate": "https://tradingeconomics.com/country-list/inflation-rate",
}
for name, url in urls.items():
    df = fetch_economic_data(url)
    if df is not None:
        print(f"{name} Data:\n", df.head())

import google.generativeai as genai
from google.generativeai import caching
from kaggle_secrets import UserSecretsClient
import datetime

# Retrieve GEMINI API Key using Kaggle Secrets
user_secrets = UserSecretsClient()
gemini_api_key = user_secrets.get_secret("GEMINI")

# Validate secret retrieval
if not gemini_api_key:
    raise ValueError("GEMINI API Key not found in Kaggle Secrets. Please ensure it's set correctly.")

# Configure GEMINI API
genai.configure(api_key=gemini_api_key)

def expand_content_to_meet_tokens(dataframe, min_tokens):
    """
    Expands a DataFrame to meet the minimum token requirement for GEMINI caching.
    """
    def estimate_token_count(df):
        text = df.to_csv(index=False)
        return len(text) // 4  # Rough token estimate (1 token ~ 4 characters)

    # Duplicate rows until token count is met
    current_tokens = estimate_token_count(dataframe)
    while current_tokens < min_tokens:
        dataframe = pd.concat([dataframe, dataframe], ignore_index=True)
        current_tokens = estimate_token_count(dataframe)

    print(f"Expanded content to {current_tokens} tokens.")
    return dataframe

# Generate or expand the dataset
data = {
    "Country": ["Country A", "Country B"],
    "GDP": [1.5, 2.3],
    "Population": [1000000, 2000000],
}
original_df = pd.DataFrame(data)
expanded_df = expand_content_to_meet_tokens(original_df, 32768)

# Save expanded DataFrame to CSV
expanded_df.to_csv("expanded_content.csv", index=False)

# Upload and cache the file
try:
    # Upload file to GEMINI
    uploaded_file = genai.upload_file(path="expanded_content.csv")

    # Wait until processing is complete
    while uploaded_file.state.name == "PROCESSING":
        print("Waiting for file to finish processing...")
        time.sleep(2)
        uploaded_file = genai.get_file(uploaded_file.name)

    print(f"File uploaded successfully: {uploaded_file.uri}")

    # Create GEMINI Cache
    cache = caching.CachedContent.create(
        model="models/gemini-1.5-flash-001",
        display_name="expanded_dataset_cache",
        system_instruction="You are an economic data analyst using the cached dataset.",
        contents=[uploaded_file],
        ttl=datetime.timedelta(hours=1),  # Cache expires in 1 hour
    )

    print(f"Cache created successfully: {cache.display_name}")

except Exception as e:
    print(f"Error caching data: {e}")

!pip install feedparser
import feedparser
from google.generativeai import GenerativeModel, caching

# Function to fetch real-time headlines
def get_realtime_headlines(rss_url='https://feeds.bbci.co.uk/news/world/rss.xml', max_headlines=5):
    """
    Fetches real-time headlines from the provided RSS feed URL.
    """
    feed = feedparser.parse(rss_url)
    headlines = [entry.title for entry in feed.entries[:max_headlines]]
    return headlines

# Unified query execution function
def execute_queries(model, queries):
    """
    Executes a set of queries using the provided model.
    """
    for query in queries:
        print(f"\nQuery: {query}")
        try:
            response = model.generate_content([query])
            print("Response:", response.text)
            print("Token Usage Metadata:", response.usage_metadata)
        except Exception as e:
            print(f"Error executing query: {e}")

# Function to analyze headlines using predefined templates
def analyze_realtime_headlines(model, query_templates, rss_url='https://feeds.bbci.co.uk/news/world/rss.xml', max_headlines=5):
    """
    Fetches real-time headlines and applies query templates for analysis.
    """
    headlines = get_realtime_headlines(rss_url, max_headlines)
    if not headlines:
        print("No headlines fetched. Please check the RSS feed URL or try again later.")
        return

    print(f"Fetched {len(headlines)} headlines:")
    for i, headline in enumerate(headlines, 1):
        print(f"{i}. {headline}")

    print("\nAnalyzing headlines...")
    for headline in headlines:
        queries = [template.format(headline=headline) for template in query_templates.values()]
        execute_queries(model, queries)

# Query templates
query_templates = {
    "summarization": "Summarize the following news headline: '{headline}'",
    "categorization": "Categorize the following news headline into one of the following categories: Politics, Business, Technology, Health, Entertainment, Sports, Science, World, Other. Headline: '{headline}'",
    "impact_analysis": "Analyze the potential impact of the following news headline on the global economy: '{headline}'",
    "trend_detection": "Determine if the following news headline indicates an emerging trend: '{headline}'",
    "bias_detection": "Detect any potential bias in the following news headline and explain your reasoning: '{headline}'"
}

# Test the integration with cache
def query_with_cache(cache, templates):
    """
    Queries GEMINI using cached context and logs performance.
    """
    try:
        model = GenerativeModel.from_cached_content(cached_content=cache)
        queries = [template for template in templates.values()]
        execute_queries(model, queries)
    except Exception as e:
        print(f"Error querying with cache: {e}")

# Example usage
try:
    model = GenerativeModel(model_name="models/gemini-1.5-flash-001")
    analyze_realtime_headlines(model, query_templates)
except Exception as e:
    print(f"Error initializing or analyzing: {e}")

# Cache usage example
try:
    cache = caching.CachedContent.get("expanded_dataset_cache")
    if cache:
        query_with_cache(cache, query_templates)
except Exception as e:
    print(f"Error fetching cache: {e}")

def log_query(query, response=None, success=True, tokens=0, error_message=None):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "success": success,
        "tokens": tokens,
        "error_message": error_message,
    }
    log_data.append(log_entry)


def analyze_logs(log_data):
    metrics = {
        "total_queries": len(log_data),
        "successful_queries": sum(1 for log in log_data if log.get("success", False)),
        "error_queries": sum(1 for log in log_data if not log.get("success", False)),
        "total_tokens_used": sum(log.get("tokens", 0) for log in log_data),
        "average_tokens_per_query": 0,
        "most_frequent_errors": [],
    }
    errors = [log.get("error_message", "Unknown error") for log in log_data if not log.get("success", False)]
    token_usages = [log.get("tokens", 0) for log in log_data if log.get("success", False)]

    if token_usages:
        metrics["average_tokens_per_query"] = sum(token_usages) / len(token_usages)

    if errors:
        metrics["most_frequent_errors"] = Counter(errors).most_common(3)

    print("\n--- Log Analysis Summary ---")
    for key, value in metrics.items():
        print(f"{key.replace('_', ' ').capitalize()}: {value}")

    # Return the metrics directly, without unpacking
    return metrics


def execute_optimized_queries(model, headlines, query_templates, max_retries=3):
    for headline in headlines:
        print(f"\nAnalyzing Headline: {headline}")
        for key, template in query_templates.items():
            query = template.format(headline=headline)
            retries = 0
            while retries < max_retries:
                try:
                    response = model.generate_content([query])
                    print(f"\nQuery ({key}): {query}")
                    print(f"Response: {response.text}")
                    tokens_used = getattr(response.usage_metadata, "total_tokens", 0)  # Handle missing fields gracefully
                    log_query(query, response=response.text, tokens=tokens_used)
                    break  # Exit retry loop on success
                except Exception as e:
                    retries += 1
                    print(f"Error executing query '{key}': {e} (Retry {retries}/{max_retries})")
                    log_query(query, success=False, error_message=str(e))
                    if retries == max_retries:
                        print(f"Max retries reached for query '{key}'")


# Example logs to debug anomalies
example_logs = [
    {"query": "Example query", "success": False, "tokens": 0, "error_message": "429 Resource has been exhausted"},
    {"query": "Another query", "success": False, "tokens": 0, "error_message": "Unknown field for UsageMetadata: total_tokens"},
]

# Generate performance report and resolve unpacking issues
try:
    metrics = analyze_logs(example_logs)
    print("\nMetrics Analysis Complete:")
    for key, value in metrics.items():
        print(f"{key}: {value}")
except Exception as e:
    print(f"Error analyzing logs: {e}")

import time
import feedparser
from collections import Counter

log_data = []

def log_query(query, response=None, success=True, tokens=0, error_message=None):
    """
    Logs details about each query execution.
    """
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "success": success,
        "tokens": tokens,
        "error_message": error_message,
    }
    log_data.append(log_entry)

def analyze_logs(log_data):
    """
    Analyzes logs and extracts key metrics.
    """
    metrics = {
        "total_queries": len(log_data),
        "successful_queries": sum(1 for log in log_data if log.get("success", False)),
        "error_queries": sum(1 for log in log_data if not log.get("success", False)),
        "total_tokens_used": sum(log.get("tokens", 0) for log in log_data),
        "average_tokens_per_query": 0,
        "most_frequent_errors": [],
    }
    errors = [log.get("error_message", "Unknown error") for log in log_data if not log.get("success", False)]
    token_usages = [log.get("tokens", 0) for log in log_data if log.get("success", False)]

    if token_usages:
        metrics["average_tokens_per_query"] = sum(token_usages) / len(token_usages)

    if errors:
        metrics["most_frequent_errors"] = Counter(errors).most_common(3)

    print("\n--- Log Analysis Summary ---")
    for key, value in metrics.items():
        print(f"{key.replace('_', ' ').capitalize()}: {value}")
    return metrics

def execute_optimized_queries(model, headlines, query_templates, max_retries=3, backoff_factor=2):
    """
    Executes queries with enhanced retry logic and logging.
    """
    for headline in headlines:
        print(f"\nAnalyzing Headline: {headline}")
        for key, template in query_templates.items():
            query = template.format(headline=headline)
            retries = 0
            while retries < max_retries:
                try:
                    response = model.generate_content([query])
                    tokens_used = getattr(response.usage_metadata, "total_tokens", 0)
                    print(f"\nQuery ({key}): {query}")
                    print(f"Response: {response.text}")
                    log_query(query, response=response.text, tokens=tokens_used)
                    break  # Exit retry loop on success
                except Exception as e:
                    retries += 1
                    print(f"Error executing query '{key}': {e} (Retry {retries}/{max_retries})")
                    log_query(query, success=False, error_message=str(e))
                    if retries < max_retries:
                        time.sleep(backoff_factor ** retries)
                    else:
                        print(f"Max retries reached for query '{key}'")

def generate_performance_report(log_data):
    """
    Generates a performance report from logs.
    """
    metrics = analyze_logs(log_data)
    report = {
        "summary": {
            "total_queries": metrics["total_queries"],
            "successful_queries": metrics["successful_queries"],
            "error_queries": metrics["error_queries"],
            "average_tokens_per_query": metrics["average_tokens_per_query"],
        },
        "error_details": metrics["most_frequent_errors"],
    }
    print("\n--- API Performance Report ---")
    for key, value in report["summary"].items():
        print(f"{key.replace('_', ' ').capitalize()}: {value}")
    if report["error_details"]:
        print("\nMost Frequent Errors:")
        for error, count in report["error_details"]:
            print(f"- {error}: {count} occurrences")
    return report

def get_realtime_headlines(rss_url='https://feeds.bbci.co.uk/news/world/rss.xml', max_headlines=5):
    """
    Fetches real-time headlines from a given RSS feed.
    """
    feed = feedparser.parse(rss_url)
    headlines = [entry.title for entry in feed.entries[:max_headlines]]
    return headlines

def analyze_realtime_headlines(model, query_templates, rss_url='https://feeds.bbci.co.uk/news/world/rss.xml', max_headlines=5):
    """
    Analyzes real-time headlines using the pipeline.
    """
    headlines = get_realtime_headlines(rss_url, max_headlines)
    if not headlines:
        print("No headlines fetched. Please check the RSS feed URL or try again later.")
        return

    print(f"Fetched {len(headlines)} headlines:")
    for i, headline in enumerate(headlines, 1):
        print(f"{i}. {headline}")

    print("\nAnalyzing headlines...")
    execute_optimized_queries(model, headlines, query_templates)

# Example query templates
query_templates = {
    "summarization": "Summarize the following headline briefly: '{headline}'",
    "categorization": "Categorize this headline into Politics, Business, Health, or Other: '{headline}'",
    "impact_analysis": "Analyze how this headline could impact the economy: '{headline}'",
    "trend_detection": "Does this headline reflect an emerging trend? '{headline}'",
    "bias_detection": "Does this headline exhibit bias? If so, explain: '{headline}'",
}

# Example usage
try:
    model = GenerativeModel(model_name="models/gemini-1.5-flash-001")
    analyze_realtime_headlines(model, query_templates)
    generate_performance_report(log_data)
except Exception as e:
    print(f"Pipeline execution error: {e}")

import functools
import time
import feedparser

# Define a cache for query results
@functools.lru_cache(maxsize=100)  # Cache up to 100 queries
def cached_query(model, query):
    try:
        response = model.generate_content([query])
        return response.text
    except Exception as e:
        print(f"Error in cached query: {e}")
        return None


# Pre-fetch queries for potential headlines
def prefetch_queries(model, query_templates, headlines):
    print("\n--- Pre-fetching Queries ---")
    for headline in headlines:
        for key, template in query_templates.items():
            query = template.format(headline=headline)
            if not cached_query.cache_info().hits:  # Only pre-fetch if not cached
                cached_query(model, query)
                print(f"Pre-fetched query: {query}")
    print("--- Pre-fetching Complete ---\n")


# Fetch headlines and analyze with caching
def analyze_with_caching(model, query_templates, rss_url='https://feeds.bbci.co.uk/news/world/rss.xml', max_headlines=5):
    headlines = get_realtime_headlines(rss_url, max_headlines)
    if not headlines:
        print("No headlines fetched. Please check the RSS feed URL or try again later.")
        return

    # Pre-fetch queries
    prefetch_queries(model, query_templates, headlines)

    print(f"Fetched {len(headlines)} headlines:")
    for i, headline in enumerate(headlines, 1):
        print(f"{i}. {headline}")

    print("\nAnalyzing headlines...")
    for headline in headlines:
        print(f"\nAnalyzing Headline: {headline}")
        for key, template in query_templates.items():
            query = template.format(headline=headline)
            cached_result = cached_query(model, query)
            if cached_result:
                print(f"\nQuery ({key}): {query}")
                print(f"Response (from cache or API): {cached_result}")


# Example usage
try:
    model = GenerativeModel(model_name="models/gemini-1.5-flash-001")
    analyze_with_caching(model, query_templates)
except Exception as e:
    print(f"Pipeline execution error: {e}")

from collections import defaultdict

def batch_queries(headlines, query_templates):
    """
    Batch queries by their type (template) for efficient API execution.
    """
    batched_queries = defaultdict(list)
    for headline in headlines:
        for key, template in query_templates.items():
            query = {
                "type": key,  # e.g., summarization, categorization
                "query": template.format(headline=headline),
                "headline": headline
            }
            batched_queries[key].append(query)
    return batched_queries

def execute_batched_queries(model, batched_queries, max_retries=3):
    """
    Execute batched queries grouped by type using the API.
    """
    results = defaultdict(list)
    for query_type, queries in batched_queries.items():
        print(f"\nExecuting batch for: {query_type} ({len(queries)} queries)")
        batched_texts = [q["query"] for q in queries]
        retries = 0
        while retries < max_retries:
            try:
                # Call the model API with the batch of queries
                responses = model.generate_content(batched_texts)
                for query, response in zip(queries, responses):
                    results[query_type].append({
                        "headline": query["headline"],
                        "query": query["query"],
                        "response": response.text
                    })
                break  # Exit retry loop on success
            except Exception as e:
                retries += 1
                print(f"Error executing batch '{query_type}': {e} (Retry {retries}/{max_retries})")
                if retries == max_retries:
                    print(f"Max retries reached for batch '{query_type}'")
                    for query in queries:
                        results[query_type].append({
                            "headline": query["headline"],
                            "query": query["query"],
                            "response": f"Error: {e}"
                        })
    return results

def analyze_realtime_headlines_with_batching(model, query_templates, rss_url='https://feeds.bbci.co.uk/news/world/rss.xml', max_headlines=5):
    """
    Fetch and analyze headlines using batched query execution.
    """
    headlines = get_realtime_headlines(rss_url, max_headlines)
    if not headlines:
        print("No headlines fetched. Please check the RSS feed URL or try again later.")
        return

    print(f"\nFetched {len(headlines)} headlines:")
    for i, headline in enumerate(headlines, 1):
        print(f"{i}. {headline}")

    print("\nBatching and analyzing headlines...")
    batched_queries = batch_queries(headlines, query_templates)
    batched_results = execute_batched_queries(model, batched_queries)

    print("\n--- Batched Query Results ---")
    for query_type, results in batched_results.items():
        print(f"\nResults for {query_type}:")
        for result in results:
            print(f"Headline: {result['headline']}")
            print(f"Query: {result['query']}")
            print(f"Response: {result['response']}")
    return batched_results

import requests
import pandas as pd
from textblob import TextBlob
import xml.etree.ElementTree as ET
from collections import defaultdict
from sklearn.preprocessing import MinMaxScaler


class NewsSentimentAnalyzer:
    def __init__(self, rss_url="http://feeds.bbci.co.uk/news/business/rss.xml", max_headlines=5):
        self.rss_url = rss_url
        self.max_headlines = max_headlines
        self.headlines = []
        self.sentiment_df = pd.DataFrame()
        self.rag_explanation = {
            "Green": "Positive market sentiment, optimism among investors.",
            "Amber": "Neutral or uncertain sentiment, a mixed or unclear outlook.",
            "Red": "Negative sentiment, potential fear or caution among investors."
        }
        self.emoticons = [
            "😞", "😟", "😕", "😐", "🙂", "😊", "😁", "😄", "😃", "😎", "💰"
        ]  # Greed scale from pessimistic to opportunistic

    def fetch_headlines(self):
        """
        Fetch headlines from the RSS feed.
        """
        try:
            response = requests.get(self.rss_url)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            self.headlines = [item.find('title').text for item in root.findall('.//item') if item.find('title') is not None]
            self.headlines = self.headlines[:self.max_headlines]
            print(f"\nFetched {len(self.headlines)} Headlines:")
            for i, headline in enumerate(self.headlines, 1):
                print(f"{i}. {headline}")
        except Exception as e:
            print(f"Error fetching headlines: {e}")

    def analyze_sentiment(self):
        """
        Perform sentiment analysis and calculate RAG and fear index.
        """
        sentiment_data = []
        for headline in self.headlines:
            sentiment = TextBlob(headline).sentiment
            polarity, subjectivity = sentiment.polarity, sentiment.subjectivity
            rag_status = "Green" if polarity > 0.1 else "Amber" if -0.1 <= polarity <= 0.1 else "Red"
            fear_index = 10 if polarity < -0.3 else 7 if polarity < -0.2 else 4 if polarity < -0.1 else 1
            greed_emoticon = self.emoticons[min(fear_index, len(self.emoticons) - 1)]
            sentiment_data.append({
                "Headline": headline,
                "Polarity": polarity,
                "Subjectivity": subjectivity,
                "RAG_Status": rag_status,
                "Fear_Index": fear_index,
                "Greedy_Emotion": greed_emoticon
            })
        self.sentiment_df = pd.DataFrame(sentiment_data)

    def explain_rag_status(self):
        """
        Provide detailed explanations for RAG statuses.
        """
        print("\n--- RAG Status Explanation ---")
        for status, explanation in self.rag_explanation.items():
            print(f"{status}: {explanation}")

    def display_sentiment_analysis(self):
        """
        Display sentiment analysis results with emoticons and RAG explanation.
        """
        print("\n--- Sentiment Analysis Results ---")
        print(self.sentiment_df[["Headline", "RAG_Status", "Fear_Index", "Greedy_Emotion"]])
        print("\n--- Detailed RAG Explanation ---")
        self.explain_rag_status()


# Caching and Optimization (Simulated)
class GeminiLongContextCache:
    def __init__(self, max_cache_size=100):
        self.cache = {}
        self.max_cache_size = max_cache_size

    def add_to_cache(self, key, value):
        """
        Add results to the cache, respecting the maximum cache size.
        """
        if len(self.cache) >= self.max_cache_size:
            self.cache.pop(next(iter(self.cache)))  # Remove the oldest entry
        self.cache[key] = value

    def get_from_cache(self, key):
        """
        Retrieve results from the cache.
        """
        return self.cache.get(key)

    def batched_execution(self, analyzer, query_templates):
        """
        Execute batched queries with caching optimization.
        """
        batched_queries = defaultdict(list)
        for headline in analyzer.headlines:
            for key, template in query_templates.items():
                query = template.format(headline=headline)
                if query in self.cache:
                    print(f"Cache hit: {query}")
                    batched_queries[key].append(self.cache[query])
                else:
                    print(f"Cache miss: {query}")
                    batched_queries[key].append(query)
                    self.add_to_cache(query, f"Simulated Response for '{query}'")
        return batched_queries


# Example Execution
if __name__ == "__main__":
    analyzer = NewsSentimentAnalyzer(max_headlines=5)
    analyzer.fetch_headlines()

    if analyzer.headlines:
        analyzer.analyze_sentiment()

        print("\n--- Sentiment Analysis DataFrame ---")
        print(analyzer.sentiment_df)

        print("\nDisplaying Sentiment Analysis with Greedy Emotions and RAG Status...")
        analyzer.display_sentiment_analysis()

        print("\nSimulating Long-Context Caching with Gemini...")
        gemini_cache = GeminiLongContextCache()
        query_templates = {
            "Summarization": "Summarize the headline: {headline}",
            "Categorization": "Categorize the headline: {headline}"
        }
        batched_results = gemini_cache.batched_execution(analyzer, query_templates)
        print("\n--- Batched Results ---")
        for query_type, queries in batched_results.items():
            print(f"\n{query_type}:")
            for query in queries:
                print(query)

