import os
import requests
import json
from datetime import datetime, timedelta

# === Config ===
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")
INSIDER_URL = "https://api.quiverquant.com/beta/live/insiders"
HEADERS = {"Authorization": f"Bearer {QUIVER_API_KEY}"}

# === Date Filter: Last 30 days ===
date_from = (datetime.today() - timedelta(days=30)).strftime("%Y%m%d")
params = {"date": date_from}

print("\nFetching recent insider trades...")
r = requests.get(INSIDER_URL, headers=HEADERS, params=params)
if r.status_code != 200:
    raise Exception(f"QuiverQuant API error: {r.text}")

data = r.json()
print(f"✅ Retrieved {len(data)} insider records since {date_from}.")

# === DEBUG: Show first 3 raw entries ===
print("\n🔍 First 3 entries from Insider data:")
for i, entry in enumerate(data[:3]):
    print(f"  Entry {i+1}: {entry}")

# === Filter for Insider Buying ===
signals = []
for entry in data:
    try:
        ticker = entry.get("Ticker") or entry.get("symbol")
        shares = float(entry.get("Shares", 0))
        price_per_share = entry.get("PricePerShare")
        code = entry.get("AcquiredDisposedCode")

        if not ticker or not price_per_share or code not in ["A", "D"]:
            continue

        transaction_value = shares * float(price_per_share)
        if transaction_value < 10000:
            continue

        signal_type = "CALL" if code == "A" else "PUT"
        source_desc = "Insider Buy" if code == "A" else "Insider Sell"

        signals.append({
            "symbol": ticker.upper(),
            "transaction_value": transaction_value,
            "source": source_desc,
            "signal_type": signal_type,
            "signal_strength": "HIGH" if transaction_value >= 100000 else "MEDIUM",
            "date": entry.get("Date")
        })
    except Exception as e:
        print(f"⚠️ Skipped insider trade due to error: {e}")

# === Save to insider_signals.json ===
if signals:
    with open("insider_signals.json", "w") as f:
        json.dump(signals, f, indent=2)
    print(f"✅ Saved {len(signals)} insider signals to insider_signals.json")
else:
    print("⚠️ No strong insider buy signals found.")
