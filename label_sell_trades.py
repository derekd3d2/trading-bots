import pandas as pd

# Customize thresholds to your preference.
WIN_THRESHOLD = 0.01       # +1% or higher => WIN
LOSS_THRESHOLD = -0.01     # -1% or lower => LOSS

def label_sell_trades():
    """
    For each BUY in trade_history.csv, find the earliest SELL that occurs later in time.
    Calculate realized % change, then label the trade as WIN, LOSS, or NEUTRAL.
    """
    # 1. Load your trade log
    df = pd.read_csv("trade_history.csv")

    # 2. Sort by timestamp in case it's out of order
    #    Ensures we properly find the 'next' SELL after a BUY
    df = df.sort_values(by="timestamp").reset_index(drop=True)

    # Prepare a list to hold labeled data
    labeled_records = []

    # 3. Iterate through each row, focusing on BUY actions
    for i, row in df.iterrows():
        if row["action"] != "BUY":
            continue  # Skip if not a BUY

        buy_ticker = row["ticker"]
        buy_price = row["price"]
        buy_timestamp = row["timestamp"]

        # Find the next SELL for the same ticker, after this row
        sell_candidates = df[
            (df["ticker"] == buy_ticker) &
            (df["action"] == "SELL") &
            (df.index > i)
        ]

        # If no SELL found, skip (trade hasn't closed or partial closes not logged)
        if sell_candidates.empty:
            continue

        # 4. Take the earliest SELL (the first row in sell_candidates)
        first_sell = sell_candidates.iloc[0]
        sell_price = first_sell["price"]
        sell_timestamp = first_sell["timestamp"]

        # 5. Calculate percent change from buy → sell
        pct_change = ((sell_price - buy_price) / buy_price) * 100

        # 6. Determine label based on thresholds
        #    (Feel free to adjust thresholds or logic)
        if pct_change >= (WIN_THRESHOLD * 100):
            label = "WIN"
        elif pct_change <= (LOSS_THRESHOLD * 100):
            label = "LOSS"
        else:
            label = "NEUTRAL"

        # 7. Append a labeled record
        labeled_records.append({
            "ticker": buy_ticker,
            "buy_timestamp": buy_timestamp,
            "sell_timestamp": sell_timestamp,
            "buy_price": round(buy_price, 4),
            "sell_price": round(sell_price, 4),
            "pct_change": round(pct_change, 4),
            "label": label
        })

    # 8. Convert results to DataFrame & save
    labeled_df = pd.DataFrame(labeled_records)
    labeled_df.to_csv("day_trade_labels.csv", index=False)

    print(f"✅ Labeled {len(labeled_df)} trades → day_trade_labels.csv")

if __name__ == "__main__":
    label_sell_trades()
