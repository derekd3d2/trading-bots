import praw
import requests
import os
import re
import sqlite3
import yfinance as yf
from datetime import datetime

# Load API Keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Authenticate with Reddit (Commented Out for Now)
# reddit = praw.Reddit(
#     client_id=os.getenv("REDDIT_CLIENT_ID"),
#     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
#     user_agent=os.getenv("REDDIT_USER_AGENT"),
#     username=os.getenv("REDDIT_USERNAME"),
#     password=os.getenv("REDDIT_PASSWORD"),
# )

# Setup SQLite Database for Stock Trends
DB_FILE = "stock_trends.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    sentiment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Function to Extract Stock Tickers from Text
def extract_tickers(text):
    pattern = r'\b[A-Z]{2,5}\b'
    tickers = re.findall(pattern, text)
    exclude_words = {"WSB", "YOLO", "SEC", "ETF", "CPI", "USD"}
    return [ticker for ticker in tickers if ticker not in exclude_words]

# Fetch WallStreetBets Sentiment
def get_wsb_sentiment():
    return "Skipping WSB Sentiment (No Reddit API Key)"

# Fetch Real-Time Stock Prices
def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]
        return f"{ticker} Current Price: ${price:.2f}"
    except Exception as e:
        return f"Error fetching {ticker} price: {e}"

# Generate Trading Signals
def generate_trading_signal(ticker):
    try:
        cursor.execute("SELECT sentiment FROM stock_trends WHERE ticker=? ORDER BY timestamp DESC LIMIT 3", (ticker,))
        sentiment_history = [row[0] for row in cursor.fetchall()]

        if not sentiment_history:
            return f"No sentiment data available for {ticker}."

        positive_count = sum(1 for sentiment in sentiment_history if "positive" in sentiment.lower())
        negative_count = sum(1 for sentiment in sentiment_history if "negative" in sentiment.lower())

        if positive_count > 2:
            signal = "BUY"
        elif negative_count > 2:
            signal = "SELL"
        else:
            signal = "HOLD"

        return f"{ticker} Trading Signal: {signal}"
    except Exception as e:
        return f"Error generating trading signal for {ticker}: {e}"

# Fetch News Sentiment (Disabled for Now)
def get_news_sentiment():
    return "Skipping News Sentiment (OpenAI API temporarily disabled)"

# Fetch Fear & Greed Index
def get_fear_greed_index():
    url = "https://api.alternative.me/fng/?limit=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        index_score = data["data"][0]["value"]
        return f"Current Fear & Greed Index: {index_score}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching Fear & Greed Index: {e}"

# Test Function Calls
if __name__ == "__main__":
    print(get_wsb_sentiment())
    print(get_news_sentiment())
    print(get_fear_greed_index())
    test_ticker = "AAPL"
    print(get_stock_price(test_ticker))
    print(generate_trading_signal(test_ticker))
