import os
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

# ✅ Load Alpaca API Keys
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

# ✅ Connect to Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")

# ✅ Get Yesterday's Date
yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

# ✅ Fetch Yesterday's Trades
orders = api.list_orders(status="filled", after=yesterday, until=datetime.today().strftime("%Y-%m-%d"))

# ✅ Print Results
if orders:
    for order in orders:
        print(f"{order.side.upper()} {order.qty} shares of {order.symbol} at ${order.filled_avg_price}")
else:
    print("⚠️ No trades were executed yesterday.")
