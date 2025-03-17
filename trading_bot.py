import os
import json
import alpaca_trade_api as tradeapi

# ✅ Load API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

# ✅ Connect to Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")

# ✅ Load Trade Signals with Debugging
def load_trade_signals():
    try:
        with open("trading_signals.json", "r") as file:
            signals = json.load(file)
        print(f"🔍 Loaded {len(signals)} trade signals from trading_signals.json")
        return signals
    except FileNotFoundError:
        print("⚠️ No trade signals found.")
        return []

# ✅ Check If a Stock Is Tradable
def is_tradable(ticker):
    try:
        asset = api.get_asset(ticker)
        print(f"✅ {ticker} is tradable on Alpaca.")
        return asset.tradable
    except Exception as e:
        print(f"⚠️ Skipping {ticker}: Error checking tradability - {e}")
        return False

# ✅ Execute Trades with Logging
def execute_trades():
    trade_signals = load_trade_signals()

    if not trade_signals:
        print("⚠️ No trades to execute.")
        return

    for trade in trade_signals:
        ticker = trade["ticker"]
        action = trade["action"]

        print(f"🔍 Processing {action} order for {ticker}")

        if not is_tradable(ticker):
            print(f"⚠️ Skipping {ticker}: Not tradable on Alpaca")
            continue  # Skip non-tradable stocks

        try:
            if action == "BUY":
                print(f"🚀 Placing BUY order for {ticker}")
                api.submit_order(
                    symbol=ticker,
                    qty=1,
                    side="buy",
                    type="market",
                    time_in_force="gtc"
                )

            elif action == "SELL":
                print(f"📉 Placing SELL order for {ticker}")
                api.submit_order(
                    symbol=ticker,
                    qty=1,
                    side="sell",
                    type="market",
                    time_in_force="gtc"
                )

        except Exception as e:
            print(f"❌ Error executing trade for {ticker}: {e}")

if __name__ == "__main__":
    execute_trades()
