import os
import alpaca_trade_api as tradeapi
from datetime import datetime

# ✅ Load Alpaca API Keys
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

# ✅ Connect to Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")

# ✅ Get Today's Filled Orders
today = datetime.today().strftime("%Y-%m-%d")
orders = api.list_orders(status="filled", after=today)

# ✅ Print Trades
if not orders:
    print("⚠️ No trades have been executed today.")
else:
    for order in orders:
        print(f"{order.side.upper()} {order.qty} shares of {order.symbol} at ${order.filled_avg_price}")
