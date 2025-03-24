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
    print("✅ API Key successfully loaded in ms_twitter.py")

# ✅ QuiverQuant Twitter API Endpoint
TWITTER_API_URL = "https://api.quiverquant.com/beta/live/twitter"

# ✅ Filter Parameters
TWITTER_GROWTH_THRESHOLD = 2.5
AI_THRESHOLD = 3.0
LOOKBACK_DAYS = 21
SAVE_PATH = "/home/ubuntu/trading-bots/ms_twitter_signals.json"

# ✅ Fetch Twitter Sentiment Data
print("📊 Fetching Twitter sentiment data from QuiverQuant...")
headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
resp = requests.get(TWITTER_API_URL, headers=headers)

if resp.status_code != 200:
    print(f"❌ Failed to fetch Twitter data: {resp.status_code}")
    exit()

data = resp.json()
now = datetime.utcnow()
cutoff_date = now - timedelta(days=LOOKBACK_DAYS)

print("\n🔍 Previewing first 10 entries from QuiverQuant:")
for entry in data[:10]:
    print({
        "ticker": entry.get("Ticker"),
        "pct_change": entry.get("pct_change"),
        "ai_score": entry.get("ai_score"),
        "date": entry.get("Date")
    })

buy_signals = []

for entry in data:
    try:
        ticker = entry.get("Ticker")
        pct_change = entry.get("pct_change", 0)
        ai_score = entry.get("ai_score", 0)
        date_str = entry.get("Date")
        if not (ticker and date_str):
            continue

        entry_date = datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
        if entry_date < cutoff_date:
            continue

        if pct_change >= TWITTER_GROWTH_THRESHOLD and ai_score >= AI_THRESHOLD:
            buy_signals.append({
                "ticker": ticker,
                "twitter_score": round(ai_score, 2),
                "pct_change": round(pct_change, 2),
                "followers": entry.get("Followers"),
                "last_updated": date_str
            })
    except Exception as e:
        print(f"⚠️ Error parsing Twitter entry: {e}")

# ✅ Save output
output = {"buy_signals": sorted(buy_signals, key=lambda x: x["twitter_score"], reverse=True)}

with open(SAVE_PATH, "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Saved Twitter sentiment signals to {SAVE_PATH} with {len(buy_signals)} entries.")
