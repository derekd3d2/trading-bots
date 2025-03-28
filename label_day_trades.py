import pandas as pd

# === CONFIG ===
INPUT_FILE = "trade_history.csv"
OUTPUT_FILE = "day_trade_labels.csv"
WIN_THRESHOLD = 0.01       # +1% or more = WIN
LOSS_THRESHOLD = -0.01     # -1% or less = LOSS

def label_day_trades():
    # 1. Load trade history
    df = pd.read_csv(INPUT_FILE)
    df = df.sort_values(by="timestamp").reset_index(drop=True)

    # 2. Prepare list of labeled trades
    labeled = []

    open_positions = []

    for _, row in df.iterrows():
        action = row["action"]
        ticker = row["ticker"]
        timestamp = row["timestamp"]
        price = float(row["price"])
        shares = float(row["shares"])
        reason = row.get("reason", "")

        if action == "BUY":
            open_positions.append({
                "ticker": ticker,
                "timestamp": timestamp,
                "price": price,
                "shares": shares,
                "reason": reason
            })

        elif action == "SELL":
            # Match with oldest unmatched BUY for the same ticker
            match_index = next((i for i, t in enumerate(open_positions) if t["ticker"] == ticker), None)

            if match_index is not None:
                buy = open_positions.pop(match_index)

                entry_price = buy["price"]
                exit_price = price
                change_pct = (exit_price - entry_price) / entry_price

                if change_pct >= WIN_THRESHOLD:
                    label = "WIN"
                elif change_pct <= LOSS_THRESHOLD:
                    label = "LOSS"
                else:
                    label = "NEUTRAL"

                labeled.append({
                    "ticker": ticker,
                    "buy_date": buy["timestamp"],
                    "sell_date": timestamp,
                    "entry_price": round(entry_price, 4),
                    "exit_price": round(exit_price, 4),
                    "pct_change": round(change_pct, 4),
                    "label": label
                })

    # 3. Output labeled trades
    if labeled:
        pd.DataFrame(labeled).to_csv(OUTPUT_FILE, index=False)
        print(f"\n✅ Labeled {len(labeled)} trades → {OUTPUT_FILE}")
    else:
        print("⚠️ No labeled trades found.")

if __name__ == "__main__":
    label_day_trades()
