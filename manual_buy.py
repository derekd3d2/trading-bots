import alpaca_trade_api as tradeapi
import os

# Load your Alpaca API keys
api = tradeapi.REST(
    os.getenv("APCA_API_KEY_ID"),
    os.getenv("APCA_API_SECRET_KEY"),
    base_url="https://paper-api.alpaca.markets",
    api_version="v2"
)

# ✅ Buy 10 shares of SOFI at market price
api.submit_order(
    symbol="IONQ",
    qty=10,
    side="buy",
    type="market",
    time_in_force="day"

    symbol="SOFI",
    qty=10,
    side="buy",
    type="market",
    time_in_force="day"

)

print("✅ Buy order submitted.")
