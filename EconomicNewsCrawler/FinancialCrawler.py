!pip install beautifulsoup4
!pip install requests

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob

def scrape_bbc_business_news():
    # Make a request to the Business section
    page = requests.get("https://www.bbc.co.uk/news/business")

    # Create a BeautifulSoup object
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find all the headline elements - adjust the tag and class according to actual website structure
    headlines = soup.find_all('h3', class_='lx-stream-post__header-title')

    # Process each headline
    for headline in headlines:
        text = headline.get_text()
        # Sentiment analysis
        sentiment = TextBlob(text).sentiment
        # Classifying sentiment polarity
        emotion, score = classify_emotion(sentiment.polarity)
        # Printing results
        print(f'Headline: {text}\nEmotion: {emotion}, Score: {score}/10\n')

def classify_emotion(polarity):
    # Define emotion based on polarity
    if polarity > 0.1:
        return ('positive', round(polarity * 10))
    elif polarity < -0.1:
        return ('negative', round(abs(polarity) * 10))
    else:
        return ('neutral', 5)

# Running the function
scrape_bbc_business_news()
