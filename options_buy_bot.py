# options_buy_bot.py
import json
import os
from datetime import datetime

SIGNALS_FILE = "options_signals.json"
TRADE_LOG_FILE = "option_trade_log.json"

if not os.path.exists(SIGNALS_FILE):
    print("⚠️ No signals to execute.")
    exit()

with open(SIGNALS_FILE, "r") as f:
    signals = json.load(f)

# Only BUY if not already bought (by checking trade log)
if os.path.exists(TRADE_LOG_FILE):
    with open(TRADE_LOG_FILE, "r") as f:
        existing_trades = json.load(f)
    bought_tickers = {t["ticker"] for t in existing_trades if t["action"] == "BUY"}
else:
    existing_trades = []
    bought_tickers = set()

for entry in signals:
    ticker = entry["symbol"]
    option_type = entry.get("direction", "CALL")
    contracts = entry.get("contracts", 1)
    strike = entry.get("strike", 100)
    expiration = entry.get("expiration", "2025-03-28")
    price = entry.get("estimated_amount", 250) / (contracts * 100)
    prediction = entry.get("ml_prediction", "unknown")

    if ticker in bought_tickers:
        print(f"⏭️ Already bought {ticker}, skipping.")
        continue

    trade = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": "BUY",
        "ticker": ticker,
        "option_type": option_type,
        "strike": strike,
        "expiration": expiration,
        "contracts": contracts,
        "price": round(price, 2),
        "reason": "New Signal",
        "prediction": prediction
    }

    print(f"🟢 Buying {ticker} {option_type} @ ${price:.2f}")
    existing_trades.append(trade)

# Save updated trade log
with open(TRADE_LOG_FILE, "w") as f:
    json.dump(existing_trades, f, indent=4)

print(f"✅ Logged {len(signals)} option BUY trades to {TRADE_LOG_FILE}")
