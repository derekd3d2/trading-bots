import os
import requests
import sqlite3
import json
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

# ✅ Load API Key from Environment
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

if not QUIVER_API_KEY:
    # Fallback: Load from .bashrc_custom
    load_dotenv("/home/ubuntu/.bashrc_custom")
    QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

if not QUIVER_API_KEY:
    raise ValueError("❌ API Key not found! Make sure it is set in the environment.")
else:
    print("✅ API Key successfully loaded in ms_twitter.py")

# ✅ QuiverQuant Twitter API Endpoint
TWITTER_API_URL = "https://api.quiverquant.com/beta/live/twitter"

# ✅ Setup SQLite Database
DB_FILE = "twitter_sentiment.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# ✅ Create Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS twitter_followers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    date TEXT,
    followers INTEGER,
    pct_change REAL,
    pct_change_week REAL,
    pct_change_daily REAL,
    ai_score REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ✅ Filter Parameters
TWITTER_GROWTH_THRESHOLD = 4.0
AI_THRESHOLD = 4.0

# ✅ Fetch & Store Twitter Data

def fetch_twitter_data():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    response = requests.get(TWITTER_API_URL, headers=headers)
    response.raise_for_status()
    twitter_data = response.json()

    relevant_tickers = {}
    for entry in twitter_data:
        ticker = entry["Ticker"]
        pct_change = entry["pct_change"]
        ai_score = entry.get("ai_score", 0)
        if pct_change >= TWITTER_GROWTH_THRESHOLD and ai_score >= AI_THRESHOLD:
            relevant_tickers[ticker] = ai_score
            cursor.execute("""
                INSERT INTO twitter_followers (ticker, date, followers, pct_change, pct_change_week, pct_change_daily, ai_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ticker, entry["Date"], entry["Followers"], pct_change, entry["pct_change_week"], entry["pct_change_daily"], ai_score))
    conn.commit()
    return relevant_tickers

# ✅ Save Twitter sentiment trading signals

def save_signals(signals, filename="twitter_signals.json"):
    trade_signals = []
    for ticker, ai_score in signals.items():
        trade_signals.append({"ticker": ticker, "ai_score": ai_score, "action": "BUY"})
    
    with open(filename, "w") as f:
        json.dump(trade_signals, f, indent=4)
    print(f"✅ {len(trade_signals)} Twitter sentiment trade signals saved to {filename}")

if __name__ == "__main__":
    print("📊 Fetching full list of tickers from Twitter sentiment data...")
    response = requests.get(TWITTER_API_URL, headers={"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"})
    response.raise_for_status()
    twitter_data = response.json()

    tickers = [entry["Ticker"] for entry in twitter_data]
    print("Tracked tickers from QuiverQuant Twitter API:", tickers)
