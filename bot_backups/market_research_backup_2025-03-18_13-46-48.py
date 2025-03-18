import os
import requests
import sqlite3
import yfinance as yf
import json
from datetime import datetime, timedelta
import time

# ✅ Load API Key from .bashrc_custom
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")
if not QUIVER_API_KEY:
    print("❌ API Key not found! Make sure it is set in ~/.bashrc_custom and sourced correctly.")
    exit(1)

# ✅ QuiverQuant API Endpoints
CONGRESS_API_URL = "https://api.quiverquant.com/beta/live/congresstrading"
PATENTS_API_URL = "https://api.quiverquant.com/beta/live/allpatents"
TWITTER_API_URL = "https://api.quiverquant.com/beta/live/twitter"
INSIDER_API_URL = "https://api.quiverquant.com/beta/live/insiders"

# ✅ Setup SQLite Database
DB_FILE = "market_research.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# ✅ Create Tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS congress_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    trade_type TEXT,
    congress_member TEXT,
    amount INTEGER,
    transaction_date TEXT,
    report_date TEXT,
    buy_price REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

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

cursor.execute("""
CREATE TABLE IF NOT EXISTS insider_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    trade_type TEXT,
    insider_name TEXT,
    shares INTEGER,
    share_price REAL,
    transaction_date TEXT,
    filing_date TEXT,
    total_value REAL,
    ai_score REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS patents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    patent_number TEXT,
    title TEXT,
    ipc_code TEXT,
    claims INTEGER,
    abstract TEXT,
    publication_date TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ✅ Filter Parameters
LOOKBACK_DAYS = 14  # Only consider trades within the last 14 days
MIN_SHARES_THRESHOLD = 10  # Minimum shares for a single Congress member to trigger a buy
TWITTER_GROWTH_THRESHOLD = 5.0  # Minimum % increase in followers
AI_THRESHOLD = 7.0  # AI confidence score threshold for executing trades

# ✅ Fetch & Store Twitter Data
def fetch_twitter_data():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    try:
        response = requests.get(TWITTER_API_URL, headers=headers)
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return {}

        twitter_data = response.json()
        if not twitter_data:
            print("⚠️ No Twitter data received.")
            return {}

        relevant_tickers = {}
        for entry in twitter_data:
            ticker = entry["Ticker"]
            pct_change = entry["pct_change"]
            ai_score = entry.get("ai_score", 0)  # Use AI score if available
            if pct_change >= TWITTER_GROWTH_THRESHOLD and ai_score >= AI_THRESHOLD:
                relevant_tickers[ticker] = ai_score
                cursor.execute("""
                    INSERT INTO twitter_followers (ticker, date, followers, pct_change, pct_change_week, pct_change_daily, ai_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (ticker, entry["Date"], entry["Followers"], pct_change, entry["pct_change_week"], entry["pct_change_daily"], ai_score))
        conn.commit()
        return relevant_tickers
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error while fetching Twitter data: {e}")
        return {}

# ✅ Fetch & Store Congress Trading Data
def fetch_congress_trades():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    try:
        response = requests.get(CONGRESS_API_URL, headers=headers)
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return []

        trades = response.json()
        if not trades:
            print("⚠️ No data received from QuiverQuant API.")
            return []

        traded_tickers = {}
        cutoff_date = (datetime.utcnow() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")

        for trade in trades:
            ticker = trade["Ticker"]
            transaction_date = trade["TransactionDate"]
            amount = int(float(trade["Amount"]))  # Convert to integer after float conversion

            if transaction_date < cutoff_date:
                continue  # Skip old trades

            if ticker not in traded_tickers:
                traded_tickers[ticker] = {"count": 0, "max_amount": 0}

            traded_tickers[ticker]["count"] += 1
            traded_tickers[ticker]["max_amount"] = max(traded_tickers[ticker]["max_amount"], amount)

        # ✅ Filter ONLY stocks we plan to buy
        trade_signals = []
        for ticker, data in traded_tickers.items():
            if data["count"] >= 2 or data["max_amount"] >= MIN_SHARES_THRESHOLD:
                trade_signals.append({"ticker": ticker, "action": "BUY"})

        if trade_signals:
            with open("trading_signals.json", "w") as file:
                json.dump(trade_signals, file, indent=4)
            print(f"✅ {len(trade_signals)} trade signals saved to trading_signals.json")
        else:
            print("⚠️ No qualifying Congress trades found.")

        return list(traded_tickers.keys())
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error while fetching Congress trades: {e}")
        return []


# ✅ Strategy 1: Congress Trading
def congress_trading_strategy():
    print("📊 Running Congress Trading Strategy...")
    traded_tickers = fetch_congress_trades()
    time.sleep(5)

# ✅ AI-Enhanced Twitter Sentiment Trading
def twitter_sentiment_strategy():
    print("📊 Running AI-Enhanced Twitter Sentiment Strategy...")
    tickers = fetch_twitter_data()
    trade_signals = []
    for ticker, ai_score in tickers.items():
        if ai_score >= AI_THRESHOLD:
            trade_signals.append({"ticker": ticker, "action": "BUY"})
    if trade_signals:
        with open("trading_signals.json", "a") as file:
            json.dump(trade_signals, file, indent=4)
        print(f"✅ {len(trade_signals)} AI-verified Twitter Sentiment trade signals saved to trading_signals.json")
    time.sleep(5)

# ✅ Fetch & Store Insider Trading Data
def fetch_insider_trades():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    try:
        response = requests.get(INSIDER_API_URL, headers=headers)
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return {}

        trades = response.json()
        if not trades:
            print("⚠️ No data received from Insider Trading API.")
            return {}

        relevant_tickers = {}
        for trade in trades:
            ticker = trade["Ticker"]
            shares = trade["Shares"]
            ai_score = trade.get("ai_score", 0)  # Use AI score if available
            if shares >= MIN_SHARES_THRESHOLD and ai_score >= AI_THRESHOLD:
                relevant_tickers[ticker] = ai_score
                cursor.execute("""
                    INSERT INTO insider_trades (ticker, trade_type, insider_name, shares, share_price, transaction_date, filing_date, total_value, ai_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (ticker, trade["AcquiredDisposedCode"], trade["Name"], shares, trade["PricePerShare"] or 0, trade["Date"], trade["fileDate"], trade["SharesOwnedFollowing"], ai_score))
        conn.commit()
        return relevant_tickers
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error while fetching Insider trades: {e}")
        return {}


# ✅ AI-Enhanced Insider Trading Strategy
def insider_trading_strategy():
    print("📊 Running AI-Enhanced Insider Trading Strategy...")
    tickers = fetch_insider_trades()
    trade_signals = []
    for ticker, ai_score in tickers.items():
        if ai_score >= AI_THRESHOLD:
            trade_signals.append({"ticker": ticker, "action": "BUY"})
    if trade_signals:
        with open("trading_signals.json", "a") as file:
            json.dump(trade_signals, file, indent=4)
        print(f"✅ {len(trade_signals)} AI-verified Insider Trading trade signals saved to trading_signals.json")
    time.sleep(5)

# ✅ Fetch & Store Patent Data
def fetch_patents():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    try:
        response = requests.get(PATENTS_API_URL, headers=headers)
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return {}

        patents = response.json()
        if not patents:
            print("⚠️ No data received from Patent API.")
            return {}

        for patent in patents:
            cursor.execute("""
                INSERT INTO patents (ticker, patent_number, title, ipc_code, claims, abstract, publication_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (patent["Ticker"], patent["PatentNumber"], patent["Title"], patent["IPC"], patent["Claims"], patent["Abstract"], patent["Date"]))

        conn.commit()
        print("✅ Patent data updated.")
        return patents
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error while fetching Patent data: {e}")
        return {}


# ✅ AI-Enhanced Patent Trading Strategy
def patent_trading_strategy():
    print("🔬 Running AI-Enhanced Patent Trading Strategy...")
    fetch_patents()
    time.sleep(5)


# ✅ Main Execution
if __name__ == "__main__":
    congress_trading_strategy()
    twitter_sentiment_strategy()
    insider_trading_strategy()
    patent_trading_strategy()
    print("✅ All trading strategies executed successfully!")
