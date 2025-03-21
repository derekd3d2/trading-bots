import os
from dotenv import load_dotenv
import requests
import json
import sqlite3

# ✅ Load API Key from Environment
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

if not QUIVER_API_KEY:
    # Fallback: Load from .bashrc_custom
    load_dotenv("/home/ubuntu/.bashrc_custom")
    QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

if not QUIVER_API_KEY:
    raise ValueError("❌ API Key not found! Make sure it is set in the environment.")
else:
    print("✅ API Key successfully loaded in ms_wsb.py")

QUIVER_WSB_URL = "https://api.quiverquant.com/beta/live/wallstreetbets"

AI_THRESHOLD = 4.0
WSB_THRESHOLD = 0.6  # Example sentiment threshold

# Database connection
conn = sqlite3.connect('trades.db')
cursor = conn.cursor()

# Fetch WSB data
def fetch_wsb_data():
    headers = {'Authorization': f'Token {QUIVER_API_KEY}'}
    response = requests.get(QUIVER_WSB_URL, headers=headers)
    response.raise_for_status()
    wsb_data = response.json()

    relevant_tickers = {}
    for entry in wsb_data:
        ticker = entry["Ticker"]
        sentiment = entry["Sentiment"]

        if sentiment >= WSB_THRESHOLD:
            relevant_tickers[ticker] = sentiment
            cursor.execute("""
                INSERT INTO wsb_sentiment (ticker, sentiment, mentions)
                VALUES (?, ?, ?)
            """, (ticker, sentiment, entry.get("Mentions", 0)))

    conn.commit()
    return relevant_tickers

# Save trading signals
def save_signals(signals, filename):
    trade_signals = []
    for ticker, ai_score in signals.items():
        trade_signals.append({"ticker": ticker, "ai_score": ai_score, "action": "BUY"})

    with open(filename, "w") as f:
        json.dump(trade_signals, f, indent=4)
    print(f"✅ {len(trade_signals)} trade signals saved to {filename}")

if __name__ == "__main__":
    print("📊 Fetching WallStreetBets sentiment data...")
    wsb_signals = fetch_wsb_data()
    save_signals(wsb_signals, "wsb_signals.json")
