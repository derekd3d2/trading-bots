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
INSIDER_LOOKBACK_DAYS = 14
SAVE_PATH = "/home/ubuntu/trading-bots/ms_insider_signals.json"

# ✅ Fetch Insider Trading Data
print("📊 Fetching Insider trading data from QuiverQuant...")
headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
resp = requests.get(INSIDER_API_URL, headers=headers)

if resp.status_code != 200:
    print(f"❌ Failed to fetch Insider data: {resp.status_code}")
    exit()

raw_data = resp.json()
longs = {}
shorts = {}

now = datetime.utcnow()
cutoff_date = now - timedelta(days=INSIDER_LOOKBACK_DAYS)

for trade in raw_data:
    try:
        date_str = trade.get("Date")
        if not date_str:
            continue
        trade_date = datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
        if trade_date < cutoff_date:
            continue

        ticker = trade.get("Ticker")
        shares = trade.get("Shares", 0)
        tx_code = trade.get("TransactionCode", "")
        if shares < MIN_SHARES_THRESHOLD:
            continue

        if tx_code == "P":  # Purchase
            if ticker not in longs:
                longs[ticker] = {"ticker": ticker, "insider_score": 0, "last_trade": date_str}
            longs[ticker]["insider_score"] += 1
        elif tx_code == "S":  # Sale
            if ticker not in shorts:
                shorts[ticker] = {"ticker": ticker, "short_score": 0, "last_trade": date_str}
            shorts[ticker]["short_score"] += 1
    except Exception as e:
        print(f"⚠️ Error parsing insider trade: {e}")

final_output = {
    "buy_signals": sorted(longs.values(), key=lambda x: x["insider_score"], reverse=True),
    "short_signals": sorted(shorts.values(), key=lambda x: x["short_score"], reverse=True)
}

with open(SAVE_PATH, "w") as f:
    json.dump(final_output, f, indent=2)

print(f"✅ Saved insider signals to {SAVE_PATH} with {len(longs)} buys and {len(shorts)} shorts.")
