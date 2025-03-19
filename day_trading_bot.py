import os
import json
import alpaca_trade_api as tradeapi
import yfinance as yf
from datetime import datetime, timedelta
import time

# ✅ Load API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    print("❌ API Keys not found! Make sure they are set in ~/.bashrc_custom and sourced correctly.")
    exit(1)

# ✅ Connect to Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")

# ✅ Trading Strategy Parameters
PROFIT_TARGET = 0.015  # 1.5% profit target
STOP_LOSS = 0.01  # 1% stop-loss
END_OF_DAY_GAIN = 0.005  # 0.5% minimum gain at EOD
EXCLUDE_TICKERS = ["TSLA"]  # Stocks to exclude

# ✅ Load Day Trading Signals from ms_daytrading_signals.py
def load_trade_signals():
    try:
        with open("day_trading_signals.json", "r") as file:
            signals = json.load(file)
        signals = [signal for signal in signals if signal["ticker"] not in EXCLUDE_TICKERS]
        print(f"🔍 Loaded {len(signals)} day trading signals after exclusion.")
        return signals
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

# ✅ Execute Buy Orders with Fractional Shares and Dynamic Rounds
def execute_trades(round_allocation):
    buying_power = float(api.get_account().buying_power)
    allocated_capital = buying_power * round_allocation

    trade_signals = load_trade_signals()
    if not trade_signals:
        print("⚠️ No trades to execute.")
        return

    capital_per_stock = allocated_capital / len(trade_signals)

    for trade in trade_signals:
        ticker = trade["ticker"]
        current_price = get_stock_price(ticker)
        if current_price is None:
            continue

        shares_to_buy = capital_per_stock / current_price

        print(f"🚀 Buying {shares_to_buy:.4f} shares of {ticker} at {current_price}")
        try:
            api.submit_order(
                symbol=ticker,
                qty=shares_to_buy,
                side="buy",
                type="market",
                time_in_force="day"
            )
        except Exception as e:
            print(f"❌ Error executing buy for {ticker}: {e}")

# ✅ Execute Sell Logic
def check_and_sell_positions(end_of_day=False):
    positions = api.list_positions()

    for pos in positions:
        ticker = pos.symbol
        buy_price = float(pos.avg_entry_price)
        current_price = get_stock_price(ticker)

        if current_price is None:
            continue

        price_change = (current_price - buy_price) / buy_price

        if price_change >= PROFIT_TARGET:
            print(f"✅ Selling {ticker}: Profit target reached.")
            api.submit_order(symbol=ticker, qty=pos.qty, side="sell", type="market", time_in_force="day")

        elif price_change <= -STOP_LOSS:
            print(f"⚠️ Selling {ticker}: Stop-loss triggered.")
            api.submit_order(symbol=ticker, qty=pos.qty, side="sell", type="market", time_in_force="day")

        elif end_of_day and price_change >= END_OF_DAY_GAIN:
            print(f"📉 Selling {ticker} at EOD with at least 0.5% gain.")
            api.submit_order(symbol=ticker, qty=pos.qty, side="sell", type="market", time_in_force="day")

# ✅ Strategy Execution
if __name__ == "__main__":
    market_close = api.get_clock().next_close - timedelta(minutes=5)
    rounds = [0.25, 0.25, 0.25, 0.25]  # Four rounds of 25% each initially

    for allocation in rounds:
        execute_trades(allocation)
        check_and_sell_positions()
        print("🕑 Waiting 5 minutes before next round.")
        time.sleep(300)

    while datetime.utcnow() < market_close:
        execute_trades(1.0)  # Use any available capital
        check_and_sell_positions()
        print("🕑 Waiting 5 minutes before next check.")
        time.sleep(300)

    print("🚨 Market closing soon, executing EOD sales.")
    check_and_sell_positions(end_of_day=True)
    print("✅ Day trading execution complete.")
