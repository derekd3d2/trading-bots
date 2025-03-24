import os
import json
from datetime import datetime

# === Load WSB Signals ===
if not os.path.exists("wsb_signals.json"):
    print("⚠️ File wsb_signals.json not found. Exiting.")
    exit()

with open("wsb_signals.json", "r") as f:
    try:
        wsb_signals = json.load(f)
    except json.JSONDecodeError:
        print("⚠️ File wsb_signals.json is not valid JSON. Exiting.")
        exit()

# === Build Options Signals ===
options_signals = []

for signal in wsb_signals:
    try:
        symbol = signal.get("ticker")
        if not symbol:
            raise ValueError("Missing 'ticker'")

        # Dynamically set direction based on "action" clearly
        action = signal.get("action")
        if action == "BUY":
            direction = "CALL"
        elif action == "SELL":
            direction = "PUT"
        else:
            continue  # Skip unknown actions clearly

        source = "WSB"
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
        print(f"⚠️ Skipped a signal due to error: {e}")

# === Save to options_wsb_signals.json ===
if options_signals:
    with open("options_wsb_signals.json", "w") as f:
        json.dump(options_signals, f, indent=2)
    print(f"✅ Saved {len(options_signals)} WSB options signals to options_wsb_signals.json")
else:
    print("⚠️ No options signals generated.")
