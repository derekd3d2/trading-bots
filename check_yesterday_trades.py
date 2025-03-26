import os
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

# ✅ Load Alpaca API Keys
APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
APCA_BASE_URL = os.getenv("APCA_PAPER_URL", "https://paper-api.alpaca.markets")

# ✅ Connect to Alpaca API
api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_BASE_URL, api_version="v2")

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
