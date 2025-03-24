import os
import requests
import json
from datetime import datetime, timedelta

# === Config ===
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")
GOV_CONTRACT_URL = "https://api.quiverquant.com/beta/live/govcontractsall"
HEADERS = {"Authorization": f"Bearer {QUIVER_API_KEY}"}

# === Date Filter: Pull contracts from the last 30 days ===
date_from = (datetime.today() - timedelta(days=30)).strftime("%Y%m%d")
params = {"date": date_from}

print("\nFetching recent government contracts...")
r = requests.get(GOV_CONTRACT_URL, headers=HEADERS, params=params)

if r.status_code != 200:
    raise Exception(f"QuiverQuant API error: {r.text}")

data = r.json()
print(f"✅ Retrieved {len(data)} contracts since {date_from}.")

# === ADD THIS DEBUGGING LINE HERE ===
print(json.dumps(data[:3], indent=2))  # Inspect first 3 contracts

# === Filter & Build Signals ===
signals = []
for contract in data:
    try:
        ticker = contract.get("Ticker") or contract.get("symbol")
        amount = float(contract.get("Amount", 0))
        agency = contract.get("Agency")
        description = contract.get("Description")

        if not ticker or amount < 1000000:
            continue  # Skip low-value or missing ticker

        signals.append({
            "symbol": ticker.upper(),
            "amount": amount,
            "agency": agency,
            "description": description,
            "source": "Gov Contract Win",
            "signal_type": "CALL",
            "signal_strength": "HIGH" if amount > 10000000 else "MEDIUM",
            "date": contract.get("Date")
        })

    except Exception as e:
        print(f"⚠️ Skipped a contract due to error: {e}")

# === Save signals to gov_signals.json ===
if signals:
    with open("gov_signals.json", "w") as f:
        json.dump(signals, f, indent=2)
    print(f"✅ Saved {len(signals)} gov contract signals (CALL & PUT) to gov_signals.json")
else:
    print("⚠️ No strong signals found.")
