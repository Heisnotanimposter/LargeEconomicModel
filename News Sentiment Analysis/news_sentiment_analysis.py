# -*- coding: utf-8 -*-
"""News Sentiment Analysis

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/#fileId=https%3A//storage.googleapis.com/kaggle-colab-exported-notebooks/news-sentiment-analysis-91c8b674-b6ff-4f31-ae7d-590c4409bbfc.ipynb%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com/20241129/auto/storage/goog4_request%26X-Goog-Date%3D20241129T050749Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3Dad0d0be5d5f77b7ca8e2c315b387d4bd063a32180d21c8eed46b357b2bfa7a5b43c5393c01678ab5f1ed13d4a2c157ac892130a075f98ef2d420421e72518db4fb2c58f45fdda4f835029fae385044778607c9fcc0e909a510913585a2a0edee84d79c8a5920e98e292656a03178296cbed0e21372c9972c290841963198d2131b9aa317cc847c7b2fa61164f855b310de72ff0511fb2c30f444f19e1f122ddeb0a453311485c51faed9cb9db7d6d4e123e7282ea91cb55b3a6c823f3b91a2ba4f88d30c137c7ad46714a6e78b76c1629f44887c3df0219a5de7a7afa8bfba554a99fee01e4494d4c5db4e71c4974a63f7a95bcd8e69b2657300deebeb7a8549
"""

# IMPORTANT: RUN THIS CELL IN ORDER TO IMPORT YOUR KAGGLE DATA SOURCES,
# THEN FEEL FREE TO DELETE THIS CELL.
# NOTE: THIS NOTEBOOK ENVIRONMENT DIFFERS FROM KAGGLE'S PYTHON
# ENVIRONMENT SO THERE MAY BE MISSING LIBRARIES USED BY YOUR
# NOTEBOOK.
import kagglehub
mmmarchetti_sentiments_dataset_path = kagglehub.dataset_download('mmmarchetti/sentiments-dataset')

print('Data source import complete.')

"""## 1. Searching for gold inside HTML files
<p>It used to take days for financial news to spread via radio, newspapers, and word of mouth. Now, in the age of the internet, it takes seconds. Did you know news articles are <em>automatically</em> being generated from figures and earnings call streams? Hedge funds and independent traders are using data science to process this wealth of information in the quest for profit.</p>
<p>In this notebook, we will generate investing insight by applying <a href="https://en.wikipedia.org/wiki/Sentiment_analysis">sentiment analysis</a> on financial news headlines from <a href="https://finviz.com">FINVIZ.com</a>. Using this <a href="https://en.wikipedia.org/wiki/Natural_language_processing">natural language processing</a> technique, we can understand the emotion behind the headlines and predict whether the market <em>feels</em> good or bad about a stock. It would then be possible to make educated guesses on how certain stocks will perform and trade accordingly. (And hopefully, make money!)</p>
<p><img src="https://assets.datacamp.com/production/project_611/img/fb_headlines.png" alt="Facebook headlines from FINVIZ.com"></p>
<p>Why headlines? And why from FINVIZ?</p>
<ol>
<li>Headlines, which have similar length, are easier to parse and group than full articles, which vary in length.</li>
<li>FINVIZ has a list of trusted websites, and headlines from these sites tend to be more consistent in their jargon than those from independent bloggers. Consistent textual patterns will improve the sentiment analysis.</li>
</ol>
<p>As <a href="https://en.wikipedia.org/wiki/Web_scraping">web scraping</a> requires data science ethics (sending a lot of traffic to a FINVIZ's servers isn't very nice), the HTML files for Facebook and Tesla at various points in time have been downloaded. Let's import these files into memory.</p>
<p><strong>Disclaimer: Investing in the stock market involves risk and can lead to monetary loss. The content in this notebook is not to be taken as financial advice.</strong> </p>
"""

# Import libraries
from bs4 import BeautifulSoup
import os
import nltk
nltk.download('vader_lexicon')

os.listdir('../input/sentiments-dataset')

html_tables = {}

# For every table in the datasets folder...
for table_name in os.listdir('../input/sentiments-dataset'):
    #this is the path to the file. Don't touch!
    table_path = f'../input/sentiments-dataset/{table_name}'
    # Open as a python file in read-only mode
    table_file = open(table_path, "r")
    # Read the contents of the file into 'html'
    html = BeautifulSoup (table_file)
    # Find 'news-table' in the Soup and load it into 'html_table'
    html_table = html.find (id = 'news-table')
    # Add the table to our dictionary
    html_tables[table_name] = html_table

html_tables.keys ()

"""## 2. What is inside those files anyway?
<p>We've grabbed the table that contains the headlines from each stock's HTML file, but before we start parsing those tables further, we need to understand how the data in that table is structured. We have a few options for this:</p>
<ul>
<li>Open the HTML file with a text editor (preferably one with syntax highlighting, like <a href="http://www.sublimetext.com/">Sublime Text</a>) and explore it there</li>
<li>Use your browser's <a href="https://addons.mozilla.org/en-US/firefox/addon/web-developer/">webdev toolkit</a> to explore the HTML</li>
<li>Explore the headlines table here in this notebook!</li>
</ul>
<p>Let's do the third option.</p>
"""

# Read one single day of headlines
tsla = html_tables['tsla_22sep.html']

# Get all the table rows tagged in HTML with <tr> into 'tesla_tr'
tsla_tr = tsla.findAll ('tr')

print (type (tsla_tr))

print (tsla_tr [0])

# For each row...
for i, table_row in enumerate(tsla_tr):
    # Read the text of the element 'a' into 'link_text'
    link_text = table_row.a.get_text()
    # Read the text of the element 'td' into 'data_text'
    data_text = table_row.td.get_text()
    # Print the count
    print(f'File number {i+1}:')
    # Print the contents of 'link_text' and 'data_text'
    print(link_text)
    print(data_text)
    # The following exits the loop after four rows to prevent spamming the notebook, do not touch
    if i == 3:
        break

"""## 3. Extra, extra! Extract the news headlines
<p>As we saw above, the interesting data inside each table row (<code>&lt;tr&gt;</code>) is in the text inside the <code>&lt;td&gt;</code> and <code>&lt;a&gt;</code> tags. Let's now actually parse the data for <strong>all</strong> tables in a comfortable data structure.</p>
"""

# Hold the parsed news into a list
parsed_news = []
# Iterate through the news
for file_name, news_table in html_tables.items():
    # Iterate through all tr tags in 'news_table'
    for x in news_table.findAll('tr'):
        # Read the text from the tr tag into text
        text = x.get_text()
        # Split the text in the td tag into a list
        date_scrape = x.td.text.split()
        # If the length of 'date_scrape' is 1, load 'time' with the only element
        # If not, load 'date' with the 1st element and 'time' with the second
        if len(date_scrape) == 1:
            time = date_scrape[0]
        else:
            date = date_scrape[0]
            time = date_scrape[1]

        # Extract the ticker from the file name, get the string up to the 1st '_'
        ticker = file_name.split("_")[0]
        # Append ticker, date, time and headline as a list to the 'parsed_news' list
        parsed_news.append([ticker, date, time, x.a.text])

parsed_news [0]

"""## 4. Make NLTK think like a financial journalist
<p>Sentiment analysis is very sensitive to context. As an example, saying <em>"This is so addictive!"</em> often means something positive if the context is a video game you are enjoying with your friends, but it very often means something negative when we are talking about opioids. Remember that the reason we chose headlines is so we can try to extract sentiment from financial journalists, who like most professionals, have their own lingo. Let's now make NLTK think like a financial journalist by adding some new words and sentiment values to our lexicon.</p>
"""

# NLTK VADER for sentiment analysis
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# New words and values
new_words = {
    'crushes': 10,
    'beats': 5,
    'misses': -5,
    'trouble': -10,
    'falls': -100,
}
# Instantiate the sentiment intensity analyzer with the existing lexicon
vader = SentimentIntensityAnalyzer ()
# Update the lexicon
vader.lexicon.update (new_words)

"""## 5. BREAKING NEWS: NLTK Crushes Sentiment Estimates
<p>Now that we have the data and the algorithm loaded, we will get to the core of the matter: programmatically predicting sentiment out of news headlines! Luckily for us, VADER is very high level so, in this case, we will not adjust the model further<sup>*</sup> other than the lexicon additions from before.</p>
<p><sup>*</sup>VADER "out-of-the-box" with some extra lexicon would likely translate into <strong>heavy losses</strong> with real money. A real sentiment analysis tool with chances of being profitable will require a very extensive and dedicated to finance news lexicon. Furthermore, it might also not be enough using a pre-packaged model like VADER.</p>
"""

import pandas as pd
# Use these column names
columns = ['ticker', 'date', 'time', 'headline']
# Convert the list of lists into a DataFrame
scored_news = pd.DataFrame (parsed_news, columns = columns)

scored_news.head ()

# Iterate through the headlines and get the polarity scores
scores = [vader.polarity_scores (headline) for headline in scored_news ['headline'].values ]
scores_df = pd.DataFrame (scores)
# Join the DataFrames
scored_news = pd.concat ([scored_news, scores_df], axis = 1)

# Convert the date column from string to datetime
scored_news['date'] = pd.to_datetime(scored_news.date).dt.date

scored_news.head ()

"""## 6. Plot all the sentiment in subplots
<p>Now that we have the scores, let's start plotting the results. We will start by plotting the time series for the stocks we have.</p>
"""

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
plt.style.use("fivethirtyeight")
# %matplotlib inline

mean_c = scored_news.groupby (['ticker', 'date']).mean ()

mean_c

# Unstack the column ticker
mean_c = mean_c.unstack ('ticker')
# Get the cross-section of compound in the 'columns' axis
mean_c = mean_c.xs ('compound', axis = 'columns')
# Plot a bar chart with pandas
mean_c.plot.bar ()

"""## 7. Weekends and duplicates
<p>What happened to Tesla on November 22nd? Since we happen to have the headlines inside our <code>DataFrame</code>, a quick peek reveals that there are a few problems with that particular day: </p>
<ul>
<li>There are only 5 headlines for that day.</li>
<li>Two headlines are verbatim the same as another but from another news outlet.</li>
</ul>
<p>Let's clean up the dataset a bit, but not too much! While some headlines are the same news piece from different sources, the fact that they are written differently could provide different perspectives on the same story. Plus, when one piece of news is more important, it tends to get more headlines from multiple sources. What we want to get rid of is verbatim copied headlines, as these are very likely coming from the same journalist and are just being "forwarded" around, so to speak.</p>
"""

# Count the number of headlines in scored_news (store as integer)
num_news_before = scored_news ['headline'].shape [0]
# Drop duplicates based on ticker and headline
scored_news_clean = scored_news.drop_duplicates (subset = ['ticker', 'headline'], keep = 'first')
# Count number of headlines after dropping duplicates
num_news_after = scored_news_clean ['headline'].shape [0]
# Print before and after numbers to get an idea of how we did
f"Before we had {num_news_before} headlines, now we have {num_news_after}"

"""## 8. Sentiment on one single trading day and stock
<p>Just to understand the possibilities of this dataset and get a better feel of the data, let's focus on one trading day and one single stock. We will make an informative plot where we will see the smallest grain possible: headline and subscores.</p>
"""

# Set the index to ticker and date
single_day = scored_news_clean.set_index(['ticker', 'date'])

# Cross-section the fb row
single_day = single_day.xs ('fb', axis = 'rows')

# Select the 3rd of January of 2019
single_day = single_day.loc [single_day.index == '2019-01-03']

single_day = single_day.reset_index ()

single_day = single_day.drop ('date', axis = 1)

# Convert the datetime string to just the time
single_day['time'] = pd.to_datetime (single_day ['time']).dt.time

# Set the index to time and
single_day = single_day.set_index ('time')
# Sort it
single_day = single_day.sort_index()

single_day.head ()

"""## 9. Visualize the single day
<p>We will make a plot to visualize the positive, negative and neutral scores for a single day of trading and a single stock. This is just one of the many ways to visualize this dataset.</p>
"""

TITLE = "Negative, neutral, and positive sentiment for FB on 2019-01-03"
COLORS = ["red","orange", "green"]
# Drop the columns that aren't useful for the plot
plot_day = single_day.drop (['headline', 'compound'], axis = 1)
# Change the column names to 'negative', 'positive', and 'neutral'
plot_day.columns = ['negative', 'neutral', 'positive']
# Plot a stacked bar chart
plot_day.plot.bar (stacked = True, color = COLORS, title = TITLE, figsize = (10,6))

plot_day.head ()

