import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time

# === CONFIGURATION ===
TRADE_LOG_FILE = "trade_history.csv"
OUTPUT_FILE = "day_trade_labels.csv"
LABEL_LOOKBACK_DAYS = 7
WIN_THRESHOLD = 0.02  # +2%
LOSS_THRESHOLD = -0.02  # -2%

# === Load Buy Trades Only ===
df = pd.read_csv(TRADE_LOG_FILE, quotechar='"', skip_blank_lines=True, on_bad_lines='skip')
buy_trades = df[df["action"] == "BUY"]

# === Process Each Trade ===
labeled_trades = []

# === Process Each Trade ===
labeled_trades = []

for _, row in buy_trades.iterrows():
    ticker = row["ticker"]
    entry_price = row["price"]
    buy_date = datetime.fromisoformat(row["timestamp"]).date()
    target_date = buy_date + timedelta(days=LABEL_LOOKBACK_DAYS)

    if target_date > datetime.today().date():
        print(f"⏳ Skipping {ticker}: trade on {buy_date} not yet 7 days old.")
        continue

    try:
        stock = yf.Ticker(ticker)
        time.sleep(1)  # avoid rate limiting

        hist = stock.history(start=target_date, end=target_date + timedelta(days=3))
        if hist.empty:
            print(f"⚠️ No price data found for {ticker} on {target_date}")
            continue

        future_price = hist["Close"].iloc[0]
        change_pct = (future_price - entry_price) / entry_price

        if change_pct >= WIN_THRESHOLD:
            label = "WIN"
        elif change_pct <= LOSS_THRESHOLD:
            label = "LOSS"
        else:
            label = "NEUTRAL"

        labeled_trades.append({
            "ticker": ticker,
            "buy_date": buy_date.isoformat(),
            "target_date": target_date.isoformat(),
            "entry_price": round(entry_price, 4),
            "future_price": round(future_price, 4),
            "pct_change": round(change_pct, 4),
            "label": label
        })

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")
        continue

# === Save Labeled Trades ===
if labeled_trades:
    pd.DataFrame(labeled_trades).to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Labeled {len(labeled_trades)} trades → {OUTPUT_FILE}")
else:
    print("\n⚠️ No trades labeled.")
