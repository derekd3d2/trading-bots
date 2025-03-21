import os
import requests
import sqlite3
import json
from datetime import datetime, timedelta
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
    print("✅ API Key successfully loaded in ms_insider_trading.py")

# ✅ QuiverQuant Insider Trading API Endpoint
INSIDER_API_URL = "https://api.quiverquant.com/beta/live/insiders"

# ✅ Filter Parameters
MIN_SHARES_THRESHOLD = 10
AI_THRESHOLD = 4.0

# ✅ Check Recent Purchases
def recently_bought(ticker, days, strategy):
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
    trade_cursor.execute("""
        SELECT buy_date FROM trades
        WHERE ticker=? AND buy_date>=? AND bot_strategy=? AND status='OPEN'
    """, (ticker, cutoff_date, strategy))
    return trade_cursor.fetchone() is not None

# ✅ Fetch Insider Trading Data
def fetch_insider_trades():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    response = requests.get(INSIDER_API_URL, headers=headers)
    response.raise_for_status()
    trades = response.json()

    relevant_trades = {}
    for trade in trades:
        ticker = trade["Ticker"]
        shares = trade["Shares"]
        ai_score = trade.get("ai_score", 0)
        if shares >= MIN_SHARES_THRESHOLD and ai_score >= AI_THRESHOLD:
            if not recently_bought(ticker, 3, "DAY_TRADING"):
                relevant_trades[ticker] = ai_score

    return relevant_trades

# ✅ Save Insider trading signals
def save_signals(signals, filename="insider_signals.json"):
    trade_signals = []
    for ticker, ai_score in signals.items():
        trade_signals.append({"ticker": ticker, "ai_score": ai_score, "action": "BUY", "strategy": "DAY_TRADING"})

    with open(filename, "w") as f:
        json.dump(trade_signals, f, indent=4)
    print(f"✅ {len(trade_signals)} Insider trading signals saved to {filename}")

# ✅ Main execution
if __name__ == "__main__":
    print("📊 Running AI-Enhanced Insider Trading Market Research...")
    insider_signals = fetch_insider_trades()
    print("Tracked tickers from QuiverQuant Insider Trading API:", list(insider_signals.keys()))
    save_signals(insider_signals)
