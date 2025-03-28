#!/usr/bin/env python3

import json
import pandas as pd

LOG_FILE = "trade_history.json"
OUTPUT_CSV = "short_prediction_stats.csv"

def evaluate_short_predictions():
    try:
        with open(LOG_FILE, "r") as f:
            trades = json.load(f)
    except FileNotFoundError:
        print(f"❌ {LOG_FILE} not found.")
        return

    matched_trades = []

    shorts = []
    for trade in trades:
        if not isinstance(trade, dict) or "action" not in trade:
            continue
        if trade["action"] == "SHORT":
            shorts.append(trade)
        elif trade["action"] == "COVER":
            for i, s in enumerate(shorts):
                if s["ticker"] == trade["ticker"]:
                    prediction = s.get("prediction")
                    if not prediction:
                        continue

                    entry_price = s["price"]
                    exit_price = trade["price"]
                    pct_change = (entry_price - exit_price) / entry_price

                    if pct_change >= 0.01:
                        outcome = "WIN"
                    elif pct_change <= -0.01:
                        outcome = "LOSS"
                    else:
                        outcome = "NEUTRAL"

                    matched_trades.append({
                        "ticker": s["ticker"],
                        "short_date": s["timestamp"],
                        "cover_date": trade["timestamp"],
                        "entry_price": round(entry_price, 4),
                        "exit_price": round(exit_price, 4),
                        "pct_change": round(pct_change, 4),
                        "prediction": prediction,
                        "outcome": outcome
                    })

                    shorts.pop(i)
                    break

    if not matched_trades:
        print("⚠️ No matched SHORT-COVER trades with predictions found.")
        return

    df = pd.DataFrame(matched_trades)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"\n✅ Evaluated {len(df)} short trades → {OUTPUT_CSV}")

    acc = (df["prediction"] == df["outcome"]).mean()
    print(f"🎯 Accuracy: {acc:.2%}")

    win_rate = (df["outcome"] == "WIN").mean()
    pred_win_rate = (df["prediction"] == "WIN").mean()

    print(f"🏆 Actual Win Rate: {win_rate:.2%}")
    print(f"🤖 Predicted WIN Rate: {pred_win_rate:.2%}")

    print("\n📊 Win Rate by Ticker:")
    print(
        df[df["outcome"] == "WIN"]["ticker"]
        .value_counts()
        .div(df["ticker"].value_counts())
        .fillna(0)
        .sort_values(ascending=False)
        .head(10)
        .to_string()
    )

if __name__ == "__main__":
    evaluate_short_predictions()
