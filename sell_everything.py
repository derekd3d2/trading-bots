import alpaca_trade_api as tradeapi
import os

# Connect to Alpaca
api = tradeapi.REST(
    os.getenv("APCA_API_KEY"),
    os.getenv("APCA_SECRET_KEY"),
    "https://paper-api.alpaca.markets",
    api_version="v2"
)

# Get all open positions
positions = api.list_positions()

# Sell all positions immediately
for position in positions:
    try:
        api.submit_order(
            symbol=position.symbol,
            qty=abs(int(position.qty)),
            side='sell',
            type='market',
            time_in_force='day'
        )
        print(f"✅ Selling {position.qty} shares of {position.symbol}")
    except Exception as e:
        print(f"❌ Error selling {position.symbol}: {e}")
