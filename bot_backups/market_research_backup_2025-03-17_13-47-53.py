import os
import requests
import sqlite3
import yfinance as yf
from datetime import datetime

# ✅ Load API Keys
QUIVER_API_KEY = os.getenv("QUIVERQUANT_API_KEY")

# ✅ Setup SQLite Database
DB_FILE = "market_research.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# ✅ Create Congress Trades Table (Track Buy Prices)
cursor.execute("""
CREATE TABLE IF NOT EXISTS congress_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    trade_type TEXT,
    congress_member TEXT,
    amount TEXT,
    transaction_date TEXT,
    report_date TEXT,
    buy_price REAL,  -- ✅ New: Store price at purchase time
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ✅ Fetch & Store Congress Trading Data
def fetch_congress_trades():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    response = requests.get("https://api.quiverquant.com/beta/live/congresstrading", headers=headers)
    trades = response.json()

    for trade in trades:
        ticker = trade["Ticker"]
        latest_price = get_stock_price(ticker)  # ✅ Fetch current price

        cursor.execute("""
            INSERT INTO congress_trades (ticker, trade_type, congress_member, amount, transaction_date, report_date, buy_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ticker, trade["Transaction"], trade["Representative"], trade["Amount"], trade["TransactionDate"], trade["ReportDate"], latest_price))

    conn.commit()
    print("✅ Congress trading data updated.")
# ✅ Get Stock Price from Yahoo Finance
import time

def get_stock_price(ticker):
    """Fetch the latest stock price from Yahoo Finance with rate limit handling."""
    for attempt in range(3):  # ✅ Retry up to 3 times
        try:
            stock = yf.Ticker(ticker)
            history = stock.history(period="5d")

            if history.empty:
                print(f"⚠️ {ticker}: No data found, possibly delisted or incorrect format.")
                return None  # ✅ Skip stock

            latest_price = history["Close"].dropna().iloc[-1]  # ✅ Get last available price
            return latest_price

        except Exception as e:
            if "Too Many Requests" in str(e):
                print(f"⏳ Rate limit hit for {ticker}. Waiting 10 seconds before retrying...")
                time.sleep(10)  # ✅ Wait 10 seconds before retrying
            else:
                print(f"❌ Error fetching price for {ticker}: {e}")
                return None  # ✅ Skip stock on error

    print(f"❌ Failed to fetch price for {ticker} after multiple attempts.")
    return None  # ✅ Skip stock if still failing after retries

if __name__ == "__main__":
    fetch_congress_trades()
