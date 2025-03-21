import os
import alpaca_trade_api as tradeapi

# ✅ Load API Keys
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

# ✅ Connect to Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")

# ✅ Sell All Open Positions
def sell_all_positions():
    positions = api.list_positions()
    if not positions:
        print("✅ No open positions to sell.")
        return

    print(f"🔍 Found {len(positions)} open positions. Selling all...")
    for pos in positions:
        ticker = pos.symbol
        qty = pos.qty
        print(f"📉 Selling {qty} of {ticker}...")
        try:
            api.submit_order(
                symbol=ticker,
                qty=qty,
                side="sell",
                type="market",
                time_in_force="gtc"
            )
        except Exception as e:
            print(f"❌ Error selling {ticker}: {e}")

    print("✅ All positions sold.")

if __name__ == "__main__":
    sell_all_positions()
