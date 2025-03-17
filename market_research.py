import os
import requests
import sqlite3
import json
from datetime import datetime

# ✅ Load API Key
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

# ✅ QuiverQuant Congress Trading API Endpoint
CONGRESS_API_URL = "https://api.quiverquant.com/beta/live/congresstrading"

# ✅ Setup SQLite Database
DB_FILE = "market_research.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# ✅ Create Congress Trades Table (Fixed 'transaction' issue)
cursor.execute("""
CREATE TABLE IF NOT EXISTS congress_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    trade_type TEXT,  -- ✅ Renamed from 'transaction' to 'trade_type'
    congress_member TEXT,
    amount TEXT,
    transaction_date TEXT,
    report_date TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ✅ Fetch & Store Congress Trading Data
def fetch_congress_trades():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    try:
        response = requests.get(CONGRESS_API_URL, headers=headers)
        response.raise_for_status()
        trades = response.json()

        for trade in trades:
            cursor.execute("""
                INSERT INTO congress_trades (ticker, trade_type, congress_member, amount, transaction_date, report_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                trade["Ticker"], trade["Transaction"], trade["Representative"],
                trade["Amount"], trade["TransactionDate"], trade["ReportDate"]
            ))

        conn.commit()
        print("✅ Congress trading data updated.")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching Congress trades: {e}")

# ✅ Generate Trade Signals & Save to JSON
def generate_trade_signals():
    cursor.execute("SELECT ticker, trade_type FROM congress_trades ORDER BY report_date DESC LIMIT 10")
    trades = cursor.fetchall()

    trade_signals = []
    for ticker, trade_type in trades:
        if trade_type.lower() == "purchase":
            trade_signals.append({"ticker": ticker, "action": "BUY"})
        elif trade_type.lower() == "sale":
            trade_signals.append({"ticker": ticker, "action": "SELL"})

    # ✅ Save signals to a JSON file for the trading bot to read
    with open("trading_signals.json", "w") as json_file:
        json.dump(trade_signals, json_file)

    print("📊 Trade signals saved to trading_signals.json.")

if __name__ == "__main__":
    fetch_congress_trades()
    generate_trade_signals()
