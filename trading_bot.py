import os
import json
import alpaca_trade_api as tradeapi
from datetime import datetime

# ✅ Load Alpaca API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"  # Change to live URL when ready

# ✅ Connect to Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")

# ✅ Load Trade Signals
def load_trade_signals():
    try:
        with open("trading_signals.json", "r") as file:
            signals = json.load(file)
        return signals
    except FileNotFoundError:
        print("⚠️ No trade signals found.")
        return []

# ✅ Get Available Cash & Calculate Dynamic Budget
def get_trading_budget(estimated_trades_today=10):
    account = api.get_account()
    total_cash = float(account.cash)  # Convert cash balance to float
    trading_budget = total_cash * 0.95  # Use 95% of available cash

    # ✅ Estimate allocation per trade dynamically based on expected trades per day
    allocation_per_trade = trading_budget / estimated_trades_today  
    return allocation_per_trade, total_cash  # Return allocation per trade & cash available

# ✅ Check if a Stock is Tradable on Alpaca
def is_tradable(ticker):
    try:
        asset = api.get_asset(ticker)
        return asset.tradable  # Returns True if tradable, False otherwise
    except Exception:
        return False  # If asset lookup fails, assume it's not tradable

# ✅ Execute Trades with Smart Allocation
def execute_trades():
    trade_signals = load_trade_signals()
    
    if not trade_signals:
        print("⚠️ No trades to execute.")
        return

    # ✅ Predict total trades today (adjust based on trends)
    estimated_trades_today = max(len(trade_signals), 10)  # Default: 10 trades/day
    
    for trade in trade_signals:
        ticker = trade["ticker"]
        action = trade["action"]

        if not is_tradable(ticker):
            print(f"⚠️ Skipping {ticker}: Not tradable on Alpaca")
            continue  # Skip non-tradable stocks

        # ✅ Get updated available cash & new allocation per trade
        allocation_per_trade, total_cash = get_trading_budget(estimated_trades_today)

        # ✅ Get real-time price using `get_latest_trade()`
        try:
            latest_price = api.get_latest_trade(ticker).price  # ✅ Correct method
            qty = int(allocation_per_trade // latest_price)  # Whole shares only

            if qty < 1:
                print(f"⚠️ Skipping {ticker}: Not enough funds to buy even 1 share.")
                continue

            if action == "BUY":
                print(f"🚀 Placing BUY order for {ticker} - {qty} shares (${allocation_per_trade:.2f} allocated, ${total_cash:.2f} available)")
                api.submit_order(
                    symbol=ticker,
                    qty=qty,
                    side="buy",
                    type="market",
                    time_in_force="gtc"
                )

            elif action == "SELL":
                print(f"📉 Placing SELL order for {ticker} - {qty} shares (${allocation_per_trade:.2f} allocated, ${total_cash:.2f} available)")
                api.submit_order(
                    symbol=ticker,
                    qty=qty,
                    side="sell",
                    type="market",
                    time_in_force="gtc"
                )

        except Exception as e:
            print(f"❌ Error executing trade for {ticker}: {e}")

if __name__ == "__main__":
    execute_trades()
