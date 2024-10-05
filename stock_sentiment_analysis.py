# Import libraries
import praw
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import datetime

# Reddit API credentials (replace with your credentials)
reddit = praw.Reddit(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    user_agent='YOUR_USER_AGENT'
)

# Function to scrape Reddit posts
def scrape_reddit(subreddit_name, search_term, limit=100):
    posts = []
    subreddit = reddit.subreddit(subreddit_name)
    
    for submission in subreddit.search(search_term, limit=limit):
        post = {
            "title": submission.title,
            "selftext": submission.selftext,
            "created": submission.created_utc
        }
        posts.append(post)
    
    return pd.DataFrame(posts)

# Function to perform sentiment analysis
def sentiment_analysis(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    return sentiment['compound']

# Fetch stock data from Yahoo Finance
def fetch_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    stock_data['Date'] = stock_data.index
    return stock_data

# Preprocess and analyze the Reddit data
def analyze_sentiment(subreddit_name, search_term, ticker, start_date, end_date):
    # Scrape Reddit posts
    df = scrape_reddit(subreddit_name, search_term)
    
    # Convert UTC to datetime
    df['created'] = pd.to_datetime(df['created'], unit='s')
    df['content'] = df['title'] + " " + df['selftext']
    
    # Perform sentiment analysis on Reddit posts
    df['sentiment'] = df['content'].apply(sentiment_analysis)
    
    # Fetch stock data
    stock_data = fetch_stock_data(ticker, start_date, end_date)
    
    # Merge stock data and Reddit sentiment data
    merged_data = pd.merge(df, stock_data, left_on='created', right_on='Date', how='inner')
    
    return merged_data

# Visualization
def visualize_sentiment_vs_stock_price(merged_data):
    plt.figure(figsize=(14, 7))
    
    sns.lineplot(x=merged_data['Date'], y=merged_data['Close'], label='Stock Price', color='b')
    sns.lineplot(x=merged_data['Date'], y=merged_data['sentiment'], label='Sentiment', color='r')
    
    plt.title("Stock Price vs Sentiment Over Time")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.legend()
    plt.show()

# Main function to run the analysis
if __name__ == '__main__':
    # Define your parameters here
    subreddit_name = 'wallstreetbets'
    search_term = 'AAPL'
    ticker = 'AAPL'
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    
    # Run sentiment analysis
    merged_data = analyze_sentiment(subreddit_name, search_term, ticker, start_date, end_date)
    
    # Visualize the result
    visualize_sentiment_vs_stock_price(merged_data)

    # Save the merged data
    merged_data.to_csv('data/stock_sentiment_output.csv', index=False)
