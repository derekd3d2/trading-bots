import os
import json
import alpaca_trade_api as tradeapi
import yfinance as yf
from datetime import datetime, timedelta
import time

# ✅ Load API Keys
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    print("❌ API Keys not found! Make sure they are set in ~/.bashrc_custom and sourced correctly.")
    exit(1)

# ✅ Connect to Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")

# ✅ Trading Strategy Parameters
PROFIT_TARGET = 0.015  # 1.5% profit target
STOP_LOSS = 0.015  # 1.5% stop-loss
CAPITAL_USAGE = 0.90  # 90% of total capital
MAX_TRADES = 15  # Limit trades to top 10-15 stocks

TRADE_HISTORY_FILE = "/home/ubuntu/trading-bots/trade_history.json"

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

    try:
        if os.path.exists(TRADE_HISTORY_FILE):
            with open(TRADE_HISTORY_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append(log_entry)

        with open(TRADE_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)

        print(f"📝 Logged {action} of {ticker} at {price}")

        # ✅ Append to CSV as well
        csv_file = TRADE_HISTORY_FILE.replace(".json", ".csv")
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, 'a', newline='') as csvfile:
            fieldnames = ["timestamp", "action", "ticker", "shares", "price", "reason"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(log_entry)
    except Exception as e:
        print(f"⚠️ Failed to log trade: {e}")

# ✅ Load Day Trading Signals from ms_daytrading_signals.py
def load_trade_signals():
    try:
        with open("day_trading_signals.json", "r") as file:
            signals = json.load(file)
        # Select top 10-15 trades & exclude TSLA
        sorted_signals = sorted(signals, key=lambda x: x['total_score'], reverse=True)[:MAX_TRADES]
        filtered_signals = sorted_signals

        print(f"🔍 Loaded {len(filtered_signals)} high-confidence trades for today.")
        return filtered_signals
    except FileNotFoundError:
        print("⚠️ No day trading signals found.")
        return []

# ✅ Fetch Current Stock Price
def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        time.sleep(1)
        history = stock.history(period="1d")
        if history.empty:
            return None
        return history["Close"].iloc[-1]
    except Exception as e:
        print(f"❌ Error fetching price for {ticker}: {e}")
        return None

# ✅ Execute Buy Orders with Dynamic Capital Allocation
def execute_trades():
    buying_power = float(api.get_account().buying_power)
    allocated_capital = buying_power * CAPITAL_USAGE

    trade_signals = load_trade_signals()
    if not trade_signals:
        print("⚠️ No trades to execute.")
        return

    capital_per_stock = allocated_capital / len(trade_signals)

    open_positions = {pos.symbol for pos in api.list_positions()}  # Get currently held stocks

    for trade in trade_signals:
        ticker = trade["ticker"]
        if ticker in open_positions:
            print(f"⚠️ Skipping {ticker}: Already in position.")
            continue

        current_price = get_stock_price(ticker)
        if current_price is None:
            continue

        shares_to_buy = capital_per_stock / current_price

        # Check if stock is fractionable
        asset = api.get_asset(ticker)
        if shares_to_buy < 1 and not asset.fractionable:
            print(f"⚠️ Skipping {ticker}: Not fractionable, insufficient capital for 1 whole share.")
            continue

        print(f"🚀 Buying {shares_to_buy:.4f} shares of {ticker} at {current_price}")
        try:
            api.submit_order(
                symbol=ticker,
                qty=round(shares_to_buy) if not asset.fractionable else shares_to_buy,
                side="buy",
                type="market",
                time_in_force="day"
            )
            log_trade("BUY", ticker, shares_to_buy, current_price, "New Signal")
        except Exception as e:
            print(f"❌ Error executing buy for {ticker}: {e}")

# ✅ Execute Sell Logic
def check_and_sell_positions():
    positions = api.list_positions()

    for pos in positions:
        ticker = pos.symbol
        position_qty = float(pos.qty)
        if position_qty <= 0:
            print(f"⚠️ Skipping {ticker}: no shares held.")
            continue

        buy_price = float(pos.avg_entry_price)
        current_price = get_stock_price(ticker)

        if current_price is None:
            continue

        price_change = (current_price - buy_price) / buy_price

        if price_change >= PROFIT_TARGET or price_change <= -STOP_LOSS:
            # Avoid immediate re-selling after buying
            open_orders = api.list_orders(status='open', symbols=[ticker])
            if open_orders:
                print(f"⚠️ Skipping selling {ticker}: open order detected.")
                continue

            try:
                api.submit_order(
                    symbol=ticker,
                    qty=position_qty,
                    side="sell",
                    type="market",
                    time_in_force="day"
                )
                reason = "Target hit" if price_change >= PROFIT_TARGET else "Stop-loss triggered"
                log_trade("SELL", ticker, position_qty, current_price, reason)
                print(f"✅ Selling {ticker} due to {reason}.")
            except Exception as e:
                print(f"❌ Error executing sell for {ticker}: {e}")

# ✅ Strategy Execution
if __name__ == "__main__":
    execute_trades()  # Execute buys
    check_and_sell_positions()  # Execute sells
    print("✅ Day trading execution complete.")
