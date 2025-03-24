import json
import joblib
import pandas as pd

# === Load model and encoders ===
model = joblib.load("option_trade_model.pkl")
ticker_encoder = joblib.load("option_ticker_encoder.pkl")
type_encoder = joblib.load("option_type_encoder.pkl")

# === Load options signals ===
with open("options_signals.json") as f:
    signals = json.load(f)

if not signals:
    print("⚠️ No options signals found.")
    exit()

# === Prepare for prediction ===
prediction_data = []
raw_entries = []

for entry in signals:
    ticker = entry["symbol"]
    option_type = entry["direction"].upper()
    entry_price = entry.get("estimated_amount", 250)  # fallback if missing

    try:
        ticker_encoded = ticker_encoder.transform([ticker])[0]
        option_type_encoded = type_encoder.transform([option_type])[0]
    except ValueError:
        print(f"⚠️ Skipping {ticker} ({option_type}): Not seen in training.")
        continue

    # Placeholder future price = 5% change assumption for now
    dummy_future_price = entry_price * 1.05 if option_type == "CALL" else entry_price * 0.95
    pct_change = (dummy_future_price - entry_price) / entry_price

    prediction_data.append([
        ticker_encoded,
        option_type_encoded,
        entry_price,
        dummy_future_price,
        pct_change
    ])
    raw_entries.append(entry)

# === Predict ===
predictions = model.predict(prediction_data)

# === Filter only predicted WINs ===
filtered_signals = []
label_map = {2: "WIN", 1: "NEUTRAL", 0: "LOSS"}

for i, pred in enumerate(predictions):
    if pred == 2:  # WIN
        entry = raw_entries[i]
        entry["ml_prediction"] = label_map[pred]
        filtered_signals.append(entry)

# === Save filtered signals ===
with open("filtered_option_signals.json", "w") as f:
    json.dump(filtered_signals, f, indent=2)

print(f"\n✅ Filtered {len(filtered_signals)} predicted WIN options → filtered_option_signals.json")
