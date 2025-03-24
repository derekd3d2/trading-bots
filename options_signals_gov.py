import os
import json
from datetime import datetime, timedelta

# === Load Signals ===
with open("gov_signals.json", "r") as f:
    gov_signals = json.load(f)

# === Build Options Trades ===
options_signals = []

for signal in gov_signals:
    try:
        symbol = signal["symbol"]
        direction = signal["signal_type"]  # CALL or PUT dynamically
        source = f"Gov Contract - {signal['agency']}"
        buy_date = datetime.today().strftime("%Y-%m-%d")
        amount = signal["amount"]

        est_amount = 250  # Default allocation per trade
        expected_gain = round(est_amount * 0.2, 2)  # 20% projection

        options_signals.append({
            "symbol": symbol,
            "direction": direction,
            "source": source,
            "buy_date": buy_date,
            "estimated_amount": est_amount,
            "expected_gain": expected_gain,
            "signal_strength": signal["signal_strength"]
        })
    except Exception as e:
        print(f"⚠️ Skipping signal due to error: {e}")

# === Save to options_signals.json ===
if options_signals:
    with open("options_gov_signals.json", "w") as f:
        json.dump(options_signals, f, indent=2)
    print(f"✅ Saved {len(options_signals)} gov contract options signals to options_signals.json")
else:
    print("⚠️ No options signals generated.")
