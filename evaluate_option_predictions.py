import json
import pandas as pd
from collections import defaultdict

# === Load AI predictions ===
with open("options_signals.json", "r") as f:
    predictions = json.load(f)

# === Load labeled results ===
labels_df = pd.read_csv("option_trade_labels.csv")
labels_df = labels_df.set_index("ticker")

# === Initialize counters ===
result_by_source = defaultdict(lambda: {"WIN": 0, "LOSS": 0, "NEUTRAL": 0, "TOTAL": 0})
result_by_ticker = defaultdict(lambda: {"WIN": 0, "LOSS": 0, "NEUTRAL": 0, "TOTAL": 0})

# === Evaluate ===
for trade in predictions:
    ticker = trade["symbol"]
    source = trade["source"]

    if ticker not in labels_df.index:
        continue

    label = labels_df.loc[ticker, "label"]
    result_by_source[source][label] += 1
    result_by_source[source]["TOTAL"] += 1

    result_by_ticker[ticker][label] += 1
    result_by_ticker[ticker]["TOTAL"] += 1

# === Print Source Summary ===
print("\n📊 Prediction Accuracy by Source:")
for source, counts in result_by_source.items():
    win_rate = 100 * counts["WIN"] / counts["TOTAL"] if counts["TOTAL"] > 0 else 0
    print(f"{source}: WIN={counts['WIN']}, LOSS={counts['LOSS']}, NEUTRAL={counts['NEUTRAL']}, WIN RATE={win_rate:.1f}%")

# === Print Top Tickers ===
print("\n📈 Top Ticker Performance:")
sorted_tickers = sorted(result_by_ticker.items(), key=lambda x: x[1]["WIN"], reverse=True)
for ticker, counts in sorted_tickers[:10]:
    win_rate = 100 * counts["WIN"] / counts["TOTAL"] if counts["TOTAL"] > 0 else 0
    print(f"{ticker}: WIN={counts['WIN']}, LOSS={counts['LOSS']}, WIN RATE={win_rate:.1f}%")
