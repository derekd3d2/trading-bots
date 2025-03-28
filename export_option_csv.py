import json
import csv

with open("option_trade_log.json", "r") as f:
    trades = json.load(f)

with open("option_trade_labels.csv", "w", newline="") as csvfile:
    fieldnames = [
        "timestamp", "action", "ticker", "contracts", "price", "strike_date",
        "option_type", "prediction", "outcome", "entry_price", "future_price", "pct_change"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in trades:
        if row["action"] == "SELL":
            writer.writerow({
                "timestamp": row["timestamp"],
                "action": row["action"],
                "ticker": row["ticker"],
                "contracts": row["contracts"],
                "price": row["price"],
                "strike_date": row["expiration"],
                "option_type": row.get("option_type", "CALL"),
                "prediction": row.get("prediction", "unknown"),
                "outcome": row.get("outcome", "unknown"),
                "entry_price": row.get("entry_price", row["price"]),     # fallback if missing
                "future_price": row.get("future_price", row["price"]),   # fallback if missing
                "pct_change": row.get("pnl_pct", 0)
            })

print("✅ Exported ML training data with outcome → option_trade_labels.csv")
