import os
import alpaca_trade_api as tradeapi
from datetime import datetime

# ✅ Load Alpaca API Keys
APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
APCA_BASE_URL = os.getenv("APCA_PAPER_URL", "https://paper-api.alpaca.markets")

# ✅ Connect to Alpaca API
api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_BASE_URL, api_version="v2")

# ✅ Get Today's Filled Orders
today = datetime.today().strftime("%Y-%m-%d")
orders = api.list_orders(status="filled", after=today)

# ✅ Print Trades
if not orders:
    print("⚠️ No trades have been executed today.")
else:
    for order in orders:
        print(f"{order.side.upper()} {order.qty} shares of {order.symbol} at ${order.filled_avg_price}")
