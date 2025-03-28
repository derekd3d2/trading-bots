import pandas as pd

# Example thresholds for an options strategy. Modify to suit your P&L logic.
WIN_THRESHOLD = 0.20       # +20%
LOSS_THRESHOLD = -0.30     # -30%

def label_option_sell_trades():
    """
    For each OPTIONS trade in option_trade_history.csv, find the realized gain/loss 
    based on your entry vs. exit data, then assign a label (WIN, LOSS, NEUTRAL).
    """
    # 1. Load your option trades
    df = pd.read_csv("option_trade_history.csv")

    # 2. Sort by timestamp to keep chronological order
    df = df.sort_values(by="timestamp").reset_index(drop=True)

    # 3. Prepare a list to store labeled data
    labeled_records = []

    # 4. Example: Suppose your file has columns:
    #    ticker, sentiment, symbol, date, cost, type, timestamp
    #    But you might need to expand if you also store 'exit cost' or 'realized cost'.

    # If you have actual buy (open) and sell (close) events for each option, 
    # the logic is similar to your stock labeling: look for a SELL row after a BUY row.
    # If you only have one line with cost, you'll need to define how you measure final P/L.

    # Pseudocode if your file included 'action' and 'entry_exit_cost' columns:
    """
    for i, row in df.iterrows():
        if row['action'] == 'OPEN':
            # gather open cost
            open_cost = row['cost']
            ...
            # find the next 'CLOSE' row
            # compute pct change
            # label as WIN/LOSS/NEUTRAL
            labeled_records.append(...)
    """

    # For now, just illustrate a placeholder approach:
    # We'll treat each line as if it has final realized cost or P/L. 
    # Modify to match your actual data structure.
    for i, row in df.iterrows():
        # Suppose 'cost' is your net credit/debit, 
        # or 'final_outcome' is your realized P/L in % form, etc.
        # This is *highly dependent* on how you log option trades.

        # Placeholder: we treat 'cost' as if it's a final P/L ratio. 
        cost = float(row["cost"])
        if cost >= WIN_THRESHOLD:
            label = "WIN"
        elif cost <= LOSS_THRESHOLD:
            label = "LOSS"
        else:
            label = "NEUTRAL"

        labeled_records.append({
            "ticker": row["ticker"],
            "symbol": row["symbol"],
            "date": row["date"],
            "type": row["type"],
            "pl_ratio": cost,
            "label": label,
            "timestamp": row["timestamp"]
        })

    labeled_df = pd.DataFrame(labeled_records)
    labeled_df.to_csv("option_trade_labels.csv", index=False)
    print(f"✅ Labeled {len(labeled_df)} option trades → option_trade_labels.csv")

if __name__ == "__main__":
    label_option_sell_trades()
