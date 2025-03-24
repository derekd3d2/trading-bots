# Filename: ms_shorts.py
import requests
import json
from datetime import datetime, timedelta

# Load API key from environment or directly insert for now
import os
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")
headers = {"Authorization": f"Bearer {QUIVER_API_KEY}"}

# Configurable thresholds
CONGRESS_DAYS = 14
INSIDER_DAYS = 7
MIN_CONGRESS_SELLS = 2
MIN_INSIDER_SELLS = 2
TWITTER_SENTIMENT_DROP = 0.2  # 20% drop
WSB_NEGATIVE_THRESHOLD = -0.5

short_signals = []
now = datetime.now()

# Helper function to check date

def within_days(date_str, days):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return (now - dt).days <= days
    except:
        return False

# --- 1. Congress Trading: Detect big sells ---
print("Fetching Congress data...")
resp = requests.get("https://api.quiverquant.com/beta/live/congresstrading", headers=headers)
if resp.status_code == 200:
    data = resp.json()
    sell_counts = {}
    for trade in data:
        if trade["Transaction"] == "Sale" and within_days(trade["TransactionDate"], CONGRESS_DAYS):
            symbol = trade["Ticker"]
            sell_counts[symbol] = sell_counts.get(symbol, 0) + 1
    for symbol, count in sell_counts.items():
        if count >= MIN_CONGRESS_SELLS:
            short_signals.append({"symbol": symbol, "source": "Congress", "reason": f"{count} Congress sells"})
else:
    print("Congress data error", resp.status_code)

# --- 2. Insider Trading: Detect clusters of selling ---
print("Fetching Insider data...")
resp = requests.get("https://api.quiverquant.com/beta/live/insiders", headers=headers)
if resp.status_code == 200:
    data = resp.json()
    insider_sales = {}
    for trade in data:
        if trade["Transaction"] == "Sale" and within_days(trade["Date"], INSIDER_DAYS):
            symbol = trade["Ticker"]
            insider_sales.setdefault(symbol, []).append(trade)
    for symbol, trades in insider_sales.items():
        if len(trades) >= MIN_INSIDER_SELLS:
            total_value = sum(float(t.get("Value", 0) or 0) for t in trades)
            short_signals.append({"symbol": symbol, "source": "Insider", "reason": f"{len(trades)} execs sold, ${int(total_value):,}"})
else:
    print("Insider data error", resp.status_code)

# --- 3. Twitter + WSB placeholders (to be implemented next) ---
# short_signals.append({"symbol": "XYZ", "source": "Twitter", "reason": "Sentiment crash -25%"})
# short_signals.append({"symbol": "ABC", "source": "WSB", "reason": "WSB score -0.8"})

# --- Save short signals ---
with open("short_signals.json", "w") as f:
    json.dump(short_signals, f, indent=2)

print(f"✅ Found {len(short_signals)} bearish opportunities. Saved to short_signals.json")

