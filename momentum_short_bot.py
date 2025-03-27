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
PROFIT_TARGET = -0.05  # Short target: gain = negative %
STOP_LOSS = 0.03       # Short stop: loss = positive %

# Tickers to short (from yesterday's long list)
TICKERS = ["TNON", "DM", "GDHG"]

# Helper

def get_previous_close(ticker):
    bars = list(api.get_bars(ticker, tradeapi.TimeFrame.Day, limit=2, feed="iex"))
    if len(bars) < 2:
        return None
    return bars[-2].c

def is_reversal(ticker, prev_close):
    bars = list(api.get_bars(ticker, tradeapi.TimeFrame.Minute, limit=15, feed="iex"))
    if len(bars) < 2:
        return False
    today_high = max([bar.h for bar in bars])
    today_open = bars[0].o
    current = bars[-1].c
    return current < prev_close and current < today_open and today_high < prev_close * 1.03

def short_stock(ticker):
    try:
        position = api.get_position(ticker)
        print(f"Already in position: {ticker}")
        return
    except:
        pass  # Not in position

    price = float(api.get_last_quote(ticker).askprice)
    qty = int(1000 / price)
    api.submit_order(symbol=ticker, qty=qty, side="sell", type="market", time_in_force="gtc")
    print(f"SHORTING {ticker} at ${price}")

def cover_shorts():
    positions = api.list_positions()
    for p in positions:
        if p.side != "short":
            continue
        current_price = float(api.get_latest_trade(p.symbol).price)
        cost_basis = float(p.avg_entry_price)
        change = (current_price - cost_basis) / cost_basis
        if change <= PROFIT_TARGET or change >= STOP_LOSS:
            api.submit_order(symbol=p.symbol, qty=int(p.qty), side="buy", type="market", time_in_force="gtc")
            print(f"COVERING {p.symbol} at ${current_price} | P&L: {change * 100:.2f}%")

# Main

def run_short_bot():
    print("Running momentum short bot...")
    shorted = 0
    for ticker in TICKERS:
        if shorted >= MAX_POSITIONS:
            break
        prev_close = get_previous_close(ticker)
        if prev_close and is_reversal(ticker, prev_close):
            short_stock(ticker)
            shorted += 1
    cover_shorts()

if __name__ == '__main__':
    run_short_bot()
