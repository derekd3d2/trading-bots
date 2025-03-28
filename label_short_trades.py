import pandas as pd

# === Config ===
INPUT_FILE = "trade_history.csv"
OUTPUT_FILE = "short_trade_labels.csv"
WIN_THRESHOLD = 0.01        # 1% gain (downward move in stock)
LOSS_THRESHOLD = -0.01      # 1% upward loss

def label_short_trades():
    df = pd.read_csv(INPUT_FILE)
    df = df.sort_values(by="timestamp").reset_index(drop=True)

    shorts = []
    labels = []

    for i, row in df.iterrows():
        if row["action"] == "SHORT":
            shorts.append(row)
        elif row["action"] == "COVER":
            # Find matching SHORT for this COVER
            for j, s in enumerate(shorts):
                if s["ticker"] == row["ticker"]:
                    entry_price = s["price"]
                    exit_price = row["price"]
                    pct_change = (entry_price - exit_price) / entry_price  # profit if stock dropped

                    if pct_change >= WIN_THRESHOLD:
                        label = "WIN"
                    elif pct_change <= LOSS_THRESHOLD:
                        label = "LOSS"
                    else:
                        label = "NEUTRAL"

                    labels.append({
                        "ticker": s["ticker"],
                        "short_date": s["timestamp"],
                        "cover_date": row["timestamp"],
                        "entry_price": round(entry_price, 4),
                        "exit_price": round(exit_price, 4),
                        "pct_change": round(pct_change, 4),
                        "label": label
                    })

                    shorts.pop(j)
                    break  # only match one

    if labels:
        pd.DataFrame(labels).to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Labeled {len(labels)} short trades → {OUTPUT_FILE}")
    else:
        print("⚠️ No completed SHORT-COVER pairs found.")

if __name__ == "__main__":
    label_short_trades()
