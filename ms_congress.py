import requests
import json
import os
import sqlite3
from datetime import datetime, timedelta

# ✅ Fetch QuiverQuant API key from environment
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

# ✅ Centralized Trades Database
TRADE_DB_FILE = "trades.db"
trade_conn = sqlite3.connect(TRADE_DB_FILE)
trade_cursor = trade_conn.cursor()

# ✅ Filter Parameters
LOOKBACK_DAYS = 14
MIN_SHARES_THRESHOLD = 10
CONGRESS_API_URL = "https://api.quiverquant.com/beta/live/congresstrading"

# ✅ Check Recent Purchases
def recently_bought(ticker, days, strategy):
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
    trade_cursor.execute("""
        SELECT buy_date FROM trades
        WHERE ticker=? AND buy_date>=? AND bot_strategy=? AND status='OPEN'
    """, (ticker, cutoff_date, strategy))
    return trade_cursor.fetchone() is not None

# ✅ Function to fetch recent Congress trades based on detailed filtering

def fetch_congress_trades():
    headers = {"Authorization": f"Bearer {QUIVER_API_KEY}"}
    response = requests.get(CONGRESS_API_URL, headers=headers)
    response.raise_for_status()

    trades = response.json()
    traded_tickers = {}
    cutoff_date = (datetime.utcnow() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")

    for trade in trades:
        ticker = trade["Ticker"]
        transaction_date = trade["TransactionDate"]
        amount = int(float(trade["Amount"]))

        if transaction_date < cutoff_date or trade["Transaction"] != "Purchase":
            continue

        if ticker not in traded_tickers:
            traded_tickers[ticker] = {"count": 0, "max_amount": 0}

        traded_tickers[ticker]["count"] += 1
        traded_tickers[ticker]["max_amount"] = max(traded_tickers[ticker]["max_amount"], amount)

    trade_signals = []
    for ticker, data in traded_tickers.items():
        if (data["count"] >= 2 or data["max_amount"] >= MIN_SHARES_THRESHOLD) and not recently_bought(ticker, 30, "LONG"):
            trade_signals.append({"ticker": ticker, "action": "BUY", "strategy": "LONG"})

    return trade_signals

# ✅ Save Congress trading signals to JSON

def save_signals(trades, filename="congress_signals.json"):
    with open(filename, "w") as f:
        json.dump(trades, f, indent=4)
    print(f"✅ {len(trades)} Congress trade signals saved to {filename}")

# ✅ Main execution
if __name__ == "__main__":
    print("📊 Running Long-Term Congress Trading Strategy...")
    congress_trades = fetch_congress_trades()
    save_signals(congress_trades)
