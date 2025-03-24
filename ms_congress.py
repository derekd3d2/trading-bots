import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# ✅ Load API Key
load_dotenv("/home/ubuntu/.bashrc_custom")
api_key = os.getenv("QUIVER_API_KEY")
if not api_key:
    raise ValueError("❌ API Key not found. Make sure it's in your environment or .bashrc_custom")

headers = {"Authorization": f"Bearer {api_key}"}
CONGRESS_LOOKBACK_DAYS = 14
SAVE_PATH = "/home/ubuntu/trading-bots/congress_signals.json"

# ✅ Get today's date and cutoff window
now = datetime.now()
cutoff_date = now - timedelta(days=CONGRESS_LOOKBACK_DAYS)

# ✅ Fetch Congress Data
print("📱 Fetching Congress trading data from QuiverQuant...")
url = "https://api.quiverquant.com/beta/bulk/congresstrading"
resp = requests.get(url, headers=headers)

if resp.status_code != 200:
    print(f"❌ Failed to fetch Congress data: {resp.status_code}")
    exit()

raw_data = resp.json()
longs = {}
shorts = {}
options = {}

# ✅ Filter and score data
for trade in raw_data:
    try:
        date_str = trade.get("TransactionDate")
        if not date_str:
            continue
        trade_date = datetime.strptime(date_str, "%Y-%m-%d")
        if trade_date < cutoff_date:
            continue

        ticker = trade.get("Ticker")
        if not ticker:
            continue

        size = trade.get("Range", "")
        score = 1
        if "$50,001 - $100,000" in size:
            score = 2
        elif "$100,001 - $250,000" in size:
            score = 3
        elif "$250,001 - $500,000" in size:
            score = 4
        elif "$500,001 - $1,000,000" in size:
            score = 5
        elif "$1,000,001 - $5,000,000" in size:
            score = 6
        elif "$5,000,001 - $25,000,000" in size:
            score = 7

        days_ago = (now - trade_date).days
        if days_ago <= 3:
            score += 1

        # Categorize by trade type
        tx_type = trade.get("Transaction")
        desc = trade.get("Description") or ""
        desc = desc.lower()

        if "option" in desc:
            if ticker not in options:
                options[ticker] = {"ticker": ticker, "options_score": 0, "last_trade": date_str}
            options[ticker]["options_score"] += score
        elif tx_type == "Purchase":
            if ticker not in longs:
                longs[ticker] = {"ticker": ticker, "congress_score": 0, "last_trade": date_str}
            longs[ticker]["congress_score"] += score
        elif tx_type == "Sale":
            if ticker not in shorts:
                shorts[ticker] = {"ticker": ticker, "short_score": 0, "last_trade": date_str}
            shorts[ticker]["short_score"] += score

    except Exception as e:
        print(f"⚠️ Error parsing trade: {e}")

# ✅ Save combined results to file
final_output = {
    "buy_signals": sorted(longs.values(), key=lambda x: x["congress_score"], reverse=True),
    "short_signals": sorted(shorts.values(), key=lambda x: x["short_score"], reverse=True),
    "options_signals": sorted(options.values(), key=lambda x: x["options_score"], reverse=True)
}

with open(SAVE_PATH, "w") as f:
    json.dump(final_output, f, indent=2)

print(f"✅ Saved Congress signals to {SAVE_PATH} with {len(longs)} buys, {len(shorts)} shorts, and {len(options)} options trades.")
