import os
import json
from datetime import datetime

# === Load Congress Signals ===
if not os.path.exists("congress_signals.json"):
    print("⚠️ File congress_signals.json not found. Exiting.")
    exit()

with open("congress_signals.json", "r") as f:
    try:
        congress_signals = json.load(f)
    except json.JSONDecodeError:
        print("⚠️ File congress_signals.json is not valid JSON. Exiting.")
        exit()

# === DEBUG: Show first 3 raw entries ===
print("\n🔍 First 3 entries from Congress data:")
for i, entry in enumerate(congress_signals[:3]):
    print(f"  Entry {i+1}: {entry}")

# === Build Options Signals ===
options_signals = []

for signal in congress_signals:
    try:
        symbol = signal.get("symbol") or signal.get("Ticker")
        source = signal.get("source", "Congress")
        if not symbol:
            raise ValueError("Missing 'symbol' or 'Ticker'")

        direction = "CALL"
        buy_date = datetime.today().strftime("%Y-%m-%d")

        est_amount = 250
        expected_gain = round(est_amount * 0.2, 2)

        options_signals.append({
            "symbol": symbol.upper(),
            "direction": direction,
            "source": source,
            "buy_date": buy_date,
            "estimated_amount": est_amount,
            "expected_gain": expected_gain
        })
    except Exception as e:
        print(f"⚠️ Skipped signal due to error: {e}")

# === Save to options_congress_signals.json ===
if options_signals:
    with open("options_congress_signals.json", "w") as f:
        json.dump(options_signals, f, indent=2)
    print(f"✅ Saved {len(options_signals)} Congress options signals to options_congress_signals.json")
else:
    print("⚠️ No options signals generated.")
