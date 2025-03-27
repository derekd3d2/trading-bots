import os
import json
import alpaca_trade_api as tradeapi
import yfinance as yf
from datetime import datetime
import time
import signal
import sys
import csv
import sys

# ✅ Graceful shutdown on CTRL+C
def signal_handler(sig, frame):
    print("\n🛑 Shorting bot stopped by user.")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# ✅ Load Alpaca API credentials
mode = os.getenv("ALPACA_ENV", "paper")
if mode == "paper":
    ALPACA_API_KEY = os.getenv("APCA_PAPER_KEY")
    ALPACA_SECRET_KEY = os.getenv("APCA_PAPER_SECRET")
    ALPACA_BASE_URL = os.getenv("APCA_PAPER_URL", "https://paper-api.alpaca.markets")
else:
    ALPACA_API_KEY = os.getenv("APCA_LIVE_KEY")
    ALPACA_SECRET_KEY = os.getenv("APCA_LIVE_SECRET")
    ALPACA_BASE_URL = os.getenv("APCA_LIVE_URL", "https://api.alpaca.markets")

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")

# ✅ Load updated short signals directly from short_signals.json
signals_file = "/home/ubuntu/trading-bots/short_signals.json"
try:
    with open(signals_file, "r") as f:
        signals = json.load(f)
except FileNotFoundError:
    print(f"❌ {signals_file} not found. Exiting.")
    sys.exit(1)

positions = {p.symbol for p in api.list_positions() if p.side == 'short'}
open_orders = {o.symbol for o in api.list_orders(status='open') if o.side == 'sell'}
skip_tickers = positions | open_orders

# ✅ Filter signals to exclude positions/open orders and limit to top 3
signals = [s for s in signals if s["ticker"] not in skip_tickers][:3]


# ✅ Constants
SHORT_TARGET = 0.02  # 5% drop = take profit
SHORT_STOPLOSS = 0.03  # 3% rise = stop-loss
CAPITAL_USAGE = 0.15  # 15% of total capital
TRADE_LOG = "/home/ubuntu/trading-bots/trade_history.json"

# ✅ Get available capital
buying_power = float(api.get_account().buying_power)
short_capital = buying_power * CAPITAL_USAGE
capital_per_trade = short_capital / 3  # top 3 trades

# ✅ Load current short positions
positions = {p.symbol: p for p in api.list_positions() if p.side == 'short'}

# ✅ Logging function
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
        time.sleep(0.5)
        hist = stock.history(period="1d")
        if hist.empty:
            return None
        return hist["Close"].iloc[-1]
    except:
        return None

# ✅ Execute new shorts
if len(positions) + len(open_orders) >= 3:
    print("🔒 Already managing 3 short positions or pending orders. No new shorts today.")
else:
    for stock in signals:
        ticker = stock["ticker"]
        if ticker in positions:
            print(f"⚠️ Already shorting {ticker}, skipping.")
            continue

        price = get_price(ticker)
        if not price:
            print(f"❌ Could not fetch price for {ticker}")
            continue

        max_qty = int(capital_per_trade // price)
        if max_qty < 1:
            print(f"⚠️ Skipping {ticker}: not enough capital for 1 share")
            continue

        try:
            api.submit_order(
                symbol=ticker,
                qty=max_qty,
                side="sell",
                type="market",
                time_in_force="day"
            )
            print(f"🔻 Shorted {max_qty} shares of {ticker} at ${price:.2f}")
            log_trade("SHORT", ticker, max_qty, price, "Live Signal")
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
