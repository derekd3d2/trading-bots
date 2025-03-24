import os
import json
import requests
import datetime
from collections import defaultdict

# === API Config ===
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")
HEADERS = {"Authorization": f"Bearer {QUIVER_API_KEY}"}
CONGRESS_URL = "https://api.quiverquant.com/beta/bulk/congresstrading"

# === Pull Past 1 Year of Trades ===
print("\nFetching Congress trades...")
r = requests.get(CONGRESS_URL, headers=HEADERS)
if r.status_code != 200:
    raise Exception(f"QuiverQuant API Error: {r.text}")

trades = r.json()
print(f"✅ Retrieved {len(trades)} Congress trades.")

start_date = datetime.date.today() - datetime.timedelta(days=365)
returns_by_rep = defaultdict(list)

# === Analyze Past Trades ===
print("Analyzing trade returns to find top 25 most profitable Congress members...")
for trade in trades:
    try:
        ticker = trade.get("Ticker")
        rep = trade.get("Representative")
        direction = trade.get("Transaction")
        date_str = trade.get("TransactionDate")

        if not ticker or not rep or direction not in ["Purchase", "Sale (Full)", "Sale (Partial)"]:
            continue

        trade_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        if trade_date < start_date:
            continue

        day_0_price = 100  # Placeholder pricing
        day_7_price = 110
        change = (day_7_price - day_0_price) / day_0_price

        if direction.startswith("Sale"):
            change *= -1

        returns_by_rep[rep].append(change)
    except Exception:
        continue

# === Top 25 by Average Return ===
average_returns = []
for rep, changes in returns_by_rep.items():
    if len(changes) >= 5:
        avg_return = sum(changes) / len(changes)
        average_returns.append((rep, avg_return))

top_25_reps = set(sorted(average_returns, key=lambda x: x[1], reverse=True)[:25])
print(f"✅ Top 25 reps selected.")

# === Filter Recent Trades by Top Reps (CALL & PUT) ===
recent_trades = []
cutoff_date = datetime.date.today() - datetime.timedelta(days=30)
for trade in trades:
    try:
        ticker = trade.get("Ticker")
        rep = trade.get("Representative")
        direction = trade.get("Transaction")
        date_str = trade.get("TransactionDate")
        trade_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

        if (
            ticker
            and rep in dict(top_25_reps)
            and direction in ["Purchase", "Sale (Full)", "Sale (Partial)"]
            and trade_date >= cutoff_date
        ):
            signal_type = "CALL" if direction == "Purchase" else "PUT"
            recent_trades.append({
                "symbol": ticker.upper(),
                "representative": rep,
                "buy_date": date_str,
                "source": f"Congress - {rep}",
                "signal_type": signal_type
            })
    except Exception:
        continue

# === Save to congress_signals.json ===
if recent_trades:
    with open("congress_signals.json", "w") as f:
        json.dump(recent_trades, f, indent=2)
    print(f"✅ Saved {len(recent_trades)} CALL & PUT signals from top 25 reps to congress_signals.json")

    # === ADD THIS QUICK CHECK HERE ===
    call_count = sum(1 for t in recent_trades if t['signal_type'] == "CALL")
    put_count = sum(1 for t in recent_trades if t['signal_type'] == "PUT")
    print(f"CALL signals: {call_count}, PUT signals: {put_count}")

else:
    print("⚠️ No recent trades found for top reps.")
