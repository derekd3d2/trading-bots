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
GOV_LOOKBACK_DAYS = 30
SAVE_PATH = "/home/ubuntu/trading-bots/ms_gov_signals.json"

# ✅ Get today's date and cutoff window
now = datetime.now()
cutoff_date = now - timedelta(days=GOV_LOOKBACK_DAYS)

# ✅ Fetch Government Contract Data
print("📡 Fetching Government Contract data from QuiverQuant...")
url = "https://api.quiverquant.com/beta/live/govcontracts"
resp = requests.get(url, headers=headers)

if resp.status_code != 200:
    print(f"❌ Failed to fetch Government Contract data: {resp.status_code}")
    exit()

data = resp.json()
contract_signals = {}

# ✅ Score each contract

for entry in data:
    try:
        ticker = entry.get("Ticker", "").strip().upper()
        if not ticker or ticker.lower() in ["n/a", "null", "none"]:
            continue

        amount_str = entry.get("Amount", 0)
        try:
            amount = float(amount_str)
        except (TypeError, ValueError):
            continue  # Skip if amount is invalid

        date_str = entry.get("Date")
        if not date_str:
            continue
        contract_date = datetime.strptime(date_str, "%Y-%m-%d")

        # Base scoring by amount
        score = 0
        if amount >= 1_000_000_000:
            score = 10
        elif amount >= 500_000_000:
            score = 9
        elif amount >= 250_000_000:
            score = 8
        elif amount >= 100_000_000:
            score = 7
        elif amount >= 50_000_000:
            score = 6
        elif amount >= 25_000_000:
            score = 5
        elif amount >= 10_000_000:
            score = 4
        elif amount >= 5_000_000:
            score = 3
        elif amount >= 1_000_000:
            score = 2
        elif amount >= 500_000:
            score = 1

        # Add recent contract bonus
        if (now - contract_date).days <= 7:
            score += 1

        if ticker not in contract_signals:
            contract_signals[ticker] = {
                "ticker": ticker,
                "scores": [],
                "total_amount": 0,
                "recent_date": date_str,
            }

        contract_signals[ticker]["scores"].append(score)
        contract_signals[ticker]["total_amount"] += amount

    except Exception as e:
        print(f"⚠️ Error parsing contract: {e}")

# ✅ Average scores before save
for ticker in contract_signals:
    scores = contract_signals[ticker].pop("scores", [])
    contract_signals[ticker]["gov_score"] = round(sum(scores) / len(scores), 2) if scores else 0

# ✅ Save results
output = {
    "buy_signals": sorted(contract_signals.values(), key=lambda x: x["gov_score"], reverse=True)
}

with open(SAVE_PATH, "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Saved Government Contract signals to {SAVE_PATH} with {len(output['buy_signals'])} entries.")

