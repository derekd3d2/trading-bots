import os
import requests
import datetime
import csv

# QuiverQuant API setup
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")
QUIVER_URL = "https://api.quiverquant.com/beta/bulk/congresstrading"
HEADERS = {"Authorization": f"Bearer {QUIVER_API_KEY}"}

# Fetch all trades in the last 12 months
def fetch_congress_trades():
    print("Fetching full Congress trading history (last 12 months)...")
    r = requests.get(QUIVER_URL, headers=HEADERS)
    if r.status_code != 200:
        raise Exception(f"QuiverQuant API error: {r.text}")
    return r.json()

def save_trade_log():
    trades = fetch_congress_trades()
    start_date = datetime.date.today() - datetime.timedelta(days=365)
    trade_log = []

    for trade in trades:
        try:
            trade_date = datetime.datetime.strptime(trade.get("TransactionDate", ""), "%Y-%m-%d").date()
            if trade_date < start_date:
                continue

            trade_log.append({
                "representative": trade.get("Representative"),
                "ticker": trade.get("Ticker"),
                "transaction_date": trade.get("TransactionDate"),
                "transaction_type": trade.get("Transaction"),
                "range": trade.get("Range"),
                "price_change": trade.get("PriceChange")
            })

        except Exception as e:
            print(f"Skipping trade due to error: {e}")
            continue

    # Save as CSV
    if trade_log:
        with open("congress_trades_detailed.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=trade_log[0].keys())
            writer.writeheader()
            writer.writerows(trade_log)
        print(f"\n✅ Saved {len(trade_log)} trades to congress_trades_detailed.csv")
    else:
        print("No trades passed the filters.")

if __name__ == "__main__":
    save_trade_log()
