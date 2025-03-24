import os
import json
import alpaca_trade_api as tradeapi
import yfinance as yf
from datetime import datetime, timedelta
import time
import signal
import sys

# ✅ Graceful shutdown on CTRL+C
def signal_handler(sig, frame):
    print("\n🛑 Shorting bot stopped by user.")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# ✅ Load Alpaca API credentials
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")

# ✅ Shorting Rules
SHORT_TARGET = 0.02  # 2% drop = cover profit
SHORT_STOPLOSS = 0.02  # 2% rise = stop-loss
CAPITAL_USAGE = 0.40  # Using 40% of total capital for shorting

SHORT_SIGNALS_FILE = "/home/ubuntu/trading-bots/short_signals.json"
TRADE_LOG = "/home/ubuntu/trading-bots/trade_history.json"

# ✅ Load short signals
with open(SHORT_SIGNALS_FILE, "r") as f:
    signals = json.load(f)

# ✅ Get available capital
buying_power = float(api.get_account().buying_power)
short_capital = buying_power * CAPITAL_USAGE
capital_per_trade = short_capital / 10  # evenly divide capital across 10 trades

# ✅ Load current positions
positions = {p.symbol: p for p in api.list_positions() if p.side == 'short'}

# ✅ Log Trade
import csv

def log_trade(action, ticker, shares, price, reason):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "ticker": ticker,
        "shares": round(shares, 4),
        "price": round(price, 4),
        "reason": reason
    }

    if os.path.exists(TRADE_LOG):
        with open(TRADE_LOG, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(log_entry)
    with open(TRADE_LOG, "w") as f:
        json.dump(history, f, indent=4)

    csv_file = TRADE_LOG.replace(".json", ".csv")
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='') as csvfile:
        fieldnames = ["timestamp", "action", "ticker", "shares", "price", "reason"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_entry)

# ✅ Get latest price

def get_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        time.sleep(0.5)  # Reduced to speed up loop and still avoid Yahoo rate-limiting
        hist = stock.history(period="1d")
        if hist.empty:
            return None
        return hist["Close"].iloc[-1]
    except:
        return None

# ✅ Execute Short Orders, sorted by score descending
sorted_signals = sorted(signals, key=lambda x: x.get("short_score", 0), reverse=True)[:15]
remaining_capital = short_capital

for stock in sorted_signals:
    ticker = stock["ticker"]
    if ticker in positions:
        print(f"⚠️ Already shorting {ticker}, skipping.")
        continue

    price = get_price(ticker)
    if not price:
        print(f"❌ Could not fetch price for {ticker}")
        continue

    max_qty = int(capital_per_trade // price)

    print(f"💵 Capital per trade: {capital_per_trade:.2f}, Price: {price:.2f}, Qty: {max_qty}")

    if max_qty < 1:
        print(f"⚠️ Skipping {ticker}: not enough capital for 1 full share")
        continue

    try:
        api.submit_order(
            symbol=ticker,
            qty=max_qty,
            side="sell",
            type="market",
            time_in_force="day"
        )
        remaining_capital -= max_qty * price
        print(f"🔻 Shorted {max_qty} shares of {ticker} at {price:.2f}")
        log_trade("SHORT", ticker, max_qty, price, "Short Signal")
    except Exception as e:
        print(f"❌ Failed to short {ticker}: {e}")

# ✅ Review open short positions to cover
positions = {p.symbol: p for p in api.list_positions() if p.side == 'short'}
for ticker, pos in positions.items():
    price = get_price(ticker)
    if not price:
        continue

    entry = float(pos.avg_entry_price)
    qty = float(pos.qty)
    change = (entry - price) / entry

    if change >= SHORT_TARGET or change <= -SHORT_STOPLOSS:
        reason = "Covered Profit" if change >= SHORT_TARGET else "Stop-Loss Covered"
        try:
            api.submit_order(
                symbol=ticker,
                qty=qty,
                side="buy",
                type="market",
                time_in_force="day"
            )
            print(f"✅ Covered short {ticker}: {reason}")
            log_trade("COVER", ticker, qty, price, reason)
        except Exception as e:
            print(f"❌ Failed to cover {ticker}: {e}")
