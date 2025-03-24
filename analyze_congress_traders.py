import os
import requests
import time
import csv
import json
from collections import defaultdict
from operator import itemgetter

# === Quiver API Setup ===
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")
QUIVER_URL = "https://api.quiverquant.com/beta/bulk/congresstrading"
HEADERS = {"Authorization": f"Bearer {QUIVER_API_KEY}"}


# === Fetch Congress Trades ===
def fetch_congress_trades():
    print("Fetching Congress trades from QuiverQuant...")
    r = requests.get(QUIVER_URL, headers=HEADERS)
    if r.status_code != 200:
        raise Exception(f"QuiverQuant API Error: {r.text}")
    return r.json()


# === Analyze Top Congress Traders ===
def analyze_top_congress_traders():
    trades = fetch_congress_trades()
    returns_by_rep = defaultdict(list)
    trade_logs = []

    print(f"Analyzing {len(trades)} trades...")

    for trade in trades:
        try:
            ticker = trade.get("Ticker")
            rep = trade.get("Representative")
            direction = trade.get("Transaction")
            date = trade.get("TransactionDate")
            price_change = trade.get("PriceChange")

            if not ticker or not rep or direction not in ["Purchase", "Sale (Full)", "Sale (Partial)"]:
                continue
            if price_change is None:
                continue

            # Flip sign if it was a sale
            if direction.startswith("Sale"):
                price_change *= -1

            returns_by_rep[rep].append(price_change)
            trade_logs.append({
                "ticker": ticker,
                "representative": rep,
                "transaction_type": direction,
                "transaction_date": date,
                "price_change": round(price_change * 100, 2)
            })

        except Exception as e:
            print(f"Skipping trade due to error: {e}")
            continue

    # Calculate average returns
    rep_returns = []
    for rep, changes in returns_by_rep.items():
        avg_return = sum(changes) / len(changes)
        rep_returns.append({
            "representative": rep,
            "num_trades": len(changes),
            "average_return_7d": round(avg_return * 100, 2)
        })

    # Sort top 25
    top_25 = sorted(rep_returns, key=itemgetter("average_return_7d"), reverse=True)[:25]

    # Save outputs
    with open("congress_trade_returns.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=trade_logs[0].keys())
        writer.writeheader()
        writer.writerows(trade_logs)

    with open("top_25_congress.json", "w") as f:
        json.dump(top_25, f, indent=2)

    print("\n✅ Done: Saved congress_trade_returns.csv and top_25_congress.json")


if __name__ == "__main__":
    analyze_top_congress_traders()
