import json
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# === Load Model and Ticker Encoder ===
model = joblib.load("day_trade_model.pkl")
ticker_encoder = joblib.load("day_ticker_encoder.pkl")

# === Load Signals ===
with open("day_trading_signals.json") as f:
    signals = json.load(f)

if not signals:
    print("⚠️ No signals found.")
    exit()

# === Prepare for Prediction ===
data_for_prediction = []
raw_entries = []

for entry in signals:
    ticker = entry["ticker"]
    total_score = entry.get("total_score", 1.0)  # fallback if missing

    try:
        ticker_encoded = ticker_encoder.transform([ticker])[0]
    except ValueError:
        print(f"⚠️ Skipping {ticker}: not seen in training.")
        continue

    # You can add more real features later. For now:
    data_for_prediction.append([ticker_encoded, 100, 103, 0.03])  # dummy prices
    raw_entries.append(entry)

# === Predict ===
predictions = model.predict(data_for_prediction)

# === Filter to WINs Only ===
filtered_signals = []
label_map = {2: "WIN", 1: "NEUTRAL", 0: "LOSS"}

for i, pred in enumerate(predictions):
    if pred == 2:  # WIN
        entry = raw_entries[i]
        entry["ml_prediction"] = label_map[pred]
        filtered_signals.append(entry)

# === Save Output ===
with open("filtered_day_signals.json", "w") as f:
    json.dump(filtered_signals, f, indent=2)

print(f"\n✅ Filtered {len(filtered_signals)} WIN signals → filtered_day_signals.json")
