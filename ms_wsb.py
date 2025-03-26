import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ✅ Load API Key from Environment
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")
if not QUIVER_API_KEY:
    load_dotenv("/home/ubuntu/.bashrc_custom")
    QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

if not QUIVER_API_KEY:
    raise ValueError("❌ API Key not found! Make sure it is set in the environment.")
else:
    print("✅ API Key successfully loaded in ms_wsb.py")

# ✅ QuiverQuant WSB API Endpoint
WSB_API_URL = "https://api.quiverquant.com/beta/live/wallstreetbets"
SAVE_PATH = "/home/ubuntu/trading-bots/ms_wsb_signals.json"
MENTION_THRESHOLD = 5
SCORE_THRESHOLD = 0.05

# ✅ Fetch WSB Data
print("📊 Fetching WallStreetBets sentiment data from QuiverQuant...")
headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
resp = requests.get(WSB_API_URL, headers=headers)

if resp.status_code != 200:
    print(f"❌ Failed to fetch WSB data: {resp.status_code}")
    exit()

data = resp.json()

buy_signals = []

for entry in data:
    try:
        ticker = entry.get("Ticker")
        mentions = entry.get("Count", 0)
        sentiment = entry.get("Sentiment", 0)
        if not ticker:
            continue

        if mentions >= MENTION_THRESHOLD and sentiment >= SCORE_THRESHOLD:
            wsb_score = min(round(sentiment * 40 + (mentions / 5), 2), 10)
            buy_signals.append({
                "ticker": ticker,
                "wsb_score": wsb_score,
                "mentions": mentions,
                "sentiment": round(sentiment, 4)
            })
    except Exception as e:
        print(f"⚠️ Error parsing WSB entry: {e}")

# ✅ Save output
output = {"buy_signals": sorted(buy_signals, key=lambda x: x["wsb_score"], reverse=True)}

with open(SAVE_PATH, "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Saved WSB sentiment signals to {SAVE_PATH} with {len(buy_signals)} entries.")
