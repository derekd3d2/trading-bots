import os
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import pytz
import time

# === Load API keys dynamically based on ALPACA_ENV ===
mode = os.getenv("ALPACA_ENV", "paper").lower()

if mode == "live":
    ALPACA_API_KEY = os.getenv("APCA_LIVE_KEY")
    ALPACA_SECRET_KEY = os.getenv("APCA_LIVE_SECRET")
    BASE_URL = os.getenv("APCA_LIVE_URL")
elif mode == "paper":
    ALPACA_API_KEY = os.getenv("APCA_PAPER_KEY")
    ALPACA_SECRET_KEY = os.getenv("APCA_PAPER_SECRET")
    BASE_URL = os.getenv("APCA_PAPER_URL")
else:
    raise ValueError("❌ Invalid ALPACA_ENV setting. Must be 'paper' or 'live'.")

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    raise ValueError("❌ Missing Alpaca API credentials. Please check ~/.bashrc_custom and reload env.")

# Alpaca client
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')
NY = "America/New_York"

# Configs
MAX_POSITIONS = 3
TARGET_PROFIT = 0.10  # 10%
STOP_LOSS = 0.03       # 3%

# Universe - placeholder
TICKERS = ["TNON", "DM", "GDHG"]

# Helper

def get_stock_data(ticker):
    now = datetime.now(pytz.timezone(NY))
    start = (now - timedelta(minutes=15)).isoformat()
    end = now.isoformat()
    barset = api.get_bars(ticker, tradeapi.TimeFrame.Minute, start=start, end=end, limit=15, feed="iex")
    return barset

def should_buy(bars):
    if len(bars) < 2:
        return False
    change = (bars[-1].c - bars[0].o) / bars[0].o
    volume = sum([bar.v for bar in bars])
    avg_volume = volume / len(bars)
    return change > 0.05 and avg_volume > 50000

def place_order(ticker):
    try:
        position = api.get_position(ticker)
        print(f"Already in position: {ticker}")
        return
    except:
        pass  # Not in position

    quote = api.get_last_quote(ticker)
    price = quote.askprice
    qty = int(1000 / price)
    api.submit_order(symbol=ticker, qty=qty, side="buy", type="market", time_in_force="gtc")
    print(f"BUYING {ticker} at ${price}")

def manage_positions():
    positions = api.list_positions()
    for p in positions:
        current_price = float(api.get_latest_trade(p.symbol).price)
        cost_basis = float(p.avg_entry_price)
        change = (current_price - cost_basis) / cost_basis

        if change >= TARGET_PROFIT or change <= -STOP_LOSS:
            api.submit_order(symbol=p.symbol, qty=int(p.qty), side="sell", type="market", time_in_force="gtc")
            print(f"SELLING {p.symbol} at ${current_price} | P&L: {change * 100:.2f}%")

# Main

def run_bot():
    print("Running momentum long bot...")
    bought = 0
    for ticker in TICKERS:
        if bought >= MAX_POSITIONS:
            break
        bars = get_stock_data(ticker)
        if should_buy(bars):
            place_order(ticker)
            bought += 1
    manage_positions()

if __name__ == '__main__':
    run_bot()
