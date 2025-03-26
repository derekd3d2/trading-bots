import os
import json
import alpaca_trade_api as tradeapi
import yfinance as yf
from datetime import datetime, timedelta
import time

# ✅ Load API Keys
APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

if not APCA_API_KEY_ID or not APCA_API_SECRET_KEY:
    print("❌ API Keys not found! Make sure they are set in ~/.bashrc_custom and sourced correctly.")
    exit(1)

# ✅ Connect to Alpaca API
api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")

# ✅ Trading Strategy Parameters
PROFIT_TARGET = 0.03  # 3% profit target
STOP_LOSS = 0.02  # 2% loss cut-off
TIME_LIMIT_3_DAYS = 0.02  # Sell at 2% gain if held for 3 days
TIME_LIMIT_7_DAYS = 7  # Sell after 1 week if no 3% gain

# ✅ Load Trade Signals
def load_trade_signals():
    try:
        with open("trading_signals.json", "r") as file:
            signals = json.load(file)
        print(f"🔍 Loaded {len(signals)} trade signals.")
        return signals
    except FileNotFoundError:
        print("⚠️ No trade signals found.")
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

# ✅ Execute Buy Orders
def execute_trades():
    trade_signals = load_trade_signals()
    if not trade_signals:
        print("⚠️ No trades to execute.")
        return

    for trade in trade_signals:
        ticker = trade["ticker"]
        action = trade["action"]
        current_price = get_stock_price(ticker)
        if current_price is None:
            continue

        if action == "BUY":
            print(f"🚀 Buying {ticker} at {current_price}")
            try:
                api.submit_order(
                    symbol=ticker,
                    qty=1,
                    side="buy",
                    type="market",
                    time_in_force="gtc"
                )
            except Exception as e:
                print(f"❌ Error executing buy for {ticker}: {e}")

# ✅ Execute Sell Logic
def check_and_sell_positions():
    positions = api.list_positions()
    today = datetime.utcnow().date()

    for pos in positions:
        ticker = pos.symbol
        buy_price = float(pos.avg_entry_price)
        current_price = get_stock_price(ticker)
        
        # ✅ Fetch trade history and manually filter for the stock
        try:
            orders = api.list_orders(status="filled", side="buy", limit=100)  # Retrieve all filled buy orders
            buy_order = next((order for order in orders if order.symbol == ticker), None)

            if buy_order:
               buy_date = buy_order.filled_at.date()
            else:
                buy_date = today  # Assume recent buy if history is unavailable
        except Exception as e:
            print(f"⚠️ Error fetching buy date for {ticker}: {e}")
            buy_date = today  # Default to today if unknown

        days_held = (today - buy_date).days

        if current_price is None:
            continue

        price_change = (current_price - buy_price) / buy_price

        if price_change >= PROFIT_TARGET:
            print(f"✅ Selling {ticker}: 3% profit reached.")
            api.submit_order(symbol=ticker, qty=1, side="sell", type="market", time_in_force="gtc")

        elif price_change <= -STOP_LOSS:
            print(f"⚠️ Selling {ticker}: 2% stop-loss triggered.")
            api.submit_order(symbol=ticker, qty=1, side="sell", type="market", time_in_force="gtc")

        elif days_held >= 3 and price_change >= TIME_LIMIT_3_DAYS:
            print(f"📅 Selling {ticker}: 2% gain after 3 days.")
            api.submit_order(symbol=ticker, qty=1, side="sell", type="market", time_in_force="gtc")

        elif days_held >= TIME_LIMIT_7_DAYS:
            print(f"⏳ Selling {ticker}: 1 week held without hitting 3% profit.")
            api.submit_order(symbol=ticker, qty=1, side="sell", type="market", time_in_force="gtc")

# ✅ Strategy Execution
if __name__ == "__main__":
    execute_trades()
    check_and_sell_positions()
    print("✅ Trade execution process complete.")
