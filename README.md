
# RAG Visualizer and BBC Financial News Crawler

## Overview

This project involves scraping financial data from various sources and performing sentiment analysis on BBC financial news headlines. The sentiment analysis results are then visualized using a Red-Amber-Green (RAG) status indicator. The project also includes machine learning models to predict the sentiment of headlines.

## Features

- **Data Scraping**: Fetch economic data from Trading Economics.
- **Sentiment Analysis**: Analyze sentiment of BBC financial news headlines using TextBlob.
- **Visualization**: Visualize sentiment polarity distribution and RAG status distribution.
- **Machine Learning**: Train and evaluate Logistic Regression, Random Forest, and Gradient Boosting models. Combine these models using a Voting Classifier.

## Setup

### Prerequisites

Ensure you have the following installed:
- Python 3.x
- pip (Python package installer)

### Installing Required Packages

1. Clone the repository:

    ```sh
    git clone https://github.com/your-username/RAG-Visualizer-and-BBC-Financial-News-Crawler.git
    cd RAG-Visualizer-and-BBC-Financial-News-Crawler
    ```

2. Install the required Python packages:

    ```sh
    pip install -r requirements.txt
    ```

### Requirements

Ensure you have the following packages installed:

```plaintext
requests
beautifulsoup4
pandas
matplotlib
seaborn
textblob
scikit-learn
```

## Usage

### Running the Script

1. **Run the main script**:

    ```sh
    python main.py
    ```

2. The script will:
    - Fetch economic data from Trading Economics.
    - Scrape BBC financial news headlines using the RSS feed.
    - Perform sentiment analysis on the headlines.
    - Visualize the sentiment analysis results.
    - Train and evaluate machine learning models on the sentiment data.
    - Display visualizations of model performances.

## Code Explanation

### Data Scraping

Fetch economic data from Trading Economics:

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_economic_data(url, table_class):
    # ... (Function code here)
    return df

# URLs of the pages to scrape data from
urls = {
    "GDP": "https://tradingeconomics.com/country-list/gdp",
    # ... (Other URLs)
}

# Fetch data for each economic indicator
economic_data = {}
for indicator, url in urls.items():
    df = fetch_economic_data(url, table_class)
    if df is not None:
        economic_data[indicator] = df
```

### Sentiment Analysis

Scrape BBC business news and perform sentiment analysis using the RSS feed:

```python
import requests
import xml.etree.ElementTree as ET
from textblob import TextBlob
import pandas as pd

def scrape_bbc_business_news_rss():
    rss_url = "http://feeds.bbci.co.uk/news/business/rss.xml"
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)
    
    # ... (Function code here)
    return df
```

### Visualization

Visualize the sentiment polarity distribution and RAG status distribution:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Visualize sentiment polarity distribution
plt.figure(figsize=(10, 6))
sns.histplot(news_df['Polarity'], bins=20, kde=True)
plt.title('Sentiment Polarity Distribution')
plt.xlabel('Polarity')
plt.ylabel('Frequency')
plt.show()

# Visualize RAG status distribution
plt.figure(figsize=(10, 6))
sns.countplot(x='RAG_Status', data=news_df, palette=['red', 'orange', 'green'])
plt.title('RAG Status Distribution')
plt.xlabel('RAG Status')
plt.ylabel('Frequency')
plt.show()
```

### Machine Learning

Train and evaluate machine learning models:

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ... (Training and evaluation code here)
```

## Contribution

Feel free to fork this project, submit issues and pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

### Creating `requirements.txt`

To generate a `requirements.txt` file with the necessary packages, you can use the following command:

```sh
pip freeze > requirements.txt
```

### Final Project Structure
