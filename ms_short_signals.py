import json
from datetime import datetime, timedelta
import os

# ✅ Load API key (if needed for future data expansion)
from dotenv import load_dotenv
load_dotenv("/home/ubuntu/.bashrc_custom")

# ✅ Load Bearish Signals from existing files
congress_file = "/home/ubuntu/trading-bots/congress_signals.json"
insider_file = "/home/ubuntu/trading-bots/ms_insider_signals.json"
wsb_file = "/home/ubuntu/trading-bots/ms_wsb_signals.json"
save_file = "/home/ubuntu/trading-bots/short_signals.json"

short_signals = {}

# ✅ Congress: use "short_signals" block
try:
    with open(congress_file, "r") as f:
        data = json.load(f)
        for entry in data.get("short_signals", []):
            ticker = entry["ticker"]
            score = entry.get("short_score", 0)
            short_signals[ticker] = short_signals.get(ticker, 0) + score
except Exception as e:
    print(f"❌ Error loading Congress shorts: {e}")

# ✅ Insider: use "short_signals" block
try:
    with open(insider_file, "r") as f:
        data = json.load(f)
        for entry in data.get("short_signals", []):
            ticker = entry["ticker"]
            score = entry.get("short_score", 0)
            short_signals[ticker] = short_signals.get(ticker, 0) + score
except Exception as e:
    print(f"❌ Error loading Insider shorts: {e}")

# ✅ WSB: sentiment < 0 becomes bearish
try:
    with open(wsb_file, "r") as f:
        data = json.load(f)
        for entry in data.get("buy_signals", []):
            ticker = entry["ticker"]
            sentiment = entry.get("wsb_score", 0)
            if sentiment < 0:
                score = abs(sentiment)
                short_signals[ticker] = short_signals.get(ticker, 0) + score
except Exception as e:
    print(f"❌ Error loading WSB shorts: {e}")

# ✅ Format + save
formatted = [
    {"ticker": t, "short_score": round(s, 3)}
    for t, s in sorted(short_signals.items(), key=lambda x: x[1], reverse=True)
    if s > 0
]

with open(save_file, "w") as f:
    json.dump(formatted, f, indent=2)

print(f"✅ Saved {len(formatted)} short signals to {save_file}")
