import json
import joblib
import os

MODEL_FILE = "short_trade_model.pkl"
ENCODER_FILE = "short_ticker_encoder.pkl"
INPUT_FILE = "short_signals.json"
OUTPUT_FILE = "filtered_short_signals.json"

# ✅ Check for required files
if not os.path.exists(MODEL_FILE) or not os.path.exists(ENCODER_FILE):
    print("❌ Model or encoder not found. Run train_model_short.py first.")
    exit()

if not os.path.exists(INPUT_FILE):
    print("❌ short_signals.json not found. Run ms_short_signals.py first.")
    exit()

# ✅ Load model and encoder
model = joblib.load(MODEL_FILE)
ticker_encoder = joblib.load(ENCODER_FILE)

# ✅ Load short signals
with open(INPUT_FILE, "r") as f:
    raw_signals = json.load(f)

prediction_data = []
raw_entries = []

for signal in raw_signals:
    ticker = signal["ticker"]

    try:
        ticker_encoded = ticker_encoder.transform([ticker])[0]
    except ValueError:
        print(f"⚠️ Skipping {ticker}: not seen in training.")
        continue

    # Simulated pricing: assume 2% drop target
    entry_price = 100
    exit_price = entry_price * 0.98
    pct_change = (entry_price - exit_price) / entry_price

    prediction_data.append([ticker_encoded, entry_price, exit_price, pct_change])
    raw_entries.append(signal)

# ✅ Predict
predictions = model.predict(prediction_data)

# ✅ Keep only predicted WINs
filtered_signals = []
label_map = {2: "WIN", 1: "NEUTRAL", 0: "LOSS"}

for i, pred in enumerate(predictions):
    if pred == 2:
        entry = raw_entries[i]
        entry["ml_prediction"] = label_map[pred]
        filtered_signals.append(entry)

# ✅ Save result
with open(OUTPUT_FILE, "w") as f:
    json.dump(filtered_signals, f, indent=2)

print(f"\n✅ Filtered {len(filtered_signals)} WIN short signals → {OUTPUT_FILE}")
