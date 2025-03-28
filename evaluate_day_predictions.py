#!/usr/bin/env python3

import json
import pandas as pd
from collections import Counter

LOG_FILE = "trade_history.json"
OUTPUT_CSV = "day_prediction_stats.csv"

def evaluate_predictions():
    try:
        with open(LOG_FILE, "r") as f:
            trades = json.load(f)
    except FileNotFoundError:
        print(f"❌ {LOG_FILE} not found.")
        return

    eval_data = []

    for trade in trades:
        if trade.get("action") != "SELL":
            continue
        if "prediction" not in trade or "outcome" not in trade:
            continue

        eval_data.append({
            "ticker": trade["ticker"],
            "prediction": trade["prediction"],
            "outcome": trade["outcome"],
            "pnl_pct": trade.get("pnl_pct", 0)
        })

    if not eval_data:
        print("⚠️ No trades with both prediction and outcome found.")
        return

    df = pd.DataFrame(eval_data)
    df.to_csv(OUTPUT_CSV, index=False)

    # ✅ Summary
    print(f"\n✅ Evaluated {len(df)} completed trades with predictions.")

    accuracy = (df["prediction"] == df["outcome"]).mean()
    print(f"🎯 Accuracy: {accuracy:.2%}")

    win_rate = (df["outcome"] == "WIN").mean()
    print(f"🏆 Win Rate (actual): {win_rate:.2%}")

    pred_win_rate = (df["prediction"] == "WIN").mean()
    print(f"🤖 Predicted WIN rate: {pred_win_rate:.2%}")

    print("\n📊 Win Rate by Ticker:")
    win_by_ticker = df[df["outcome"] == "WIN"]["ticker"].value_counts()
    total_by_ticker = df["ticker"].value_counts()
    win_rate_by_ticker = (win_by_ticker / total_by_ticker).fillna(0).sort_values(ascending=False)

    print(win_rate_by_ticker.head(10).to_string())

if __name__ == "__main__":
    evaluate_predictions()
