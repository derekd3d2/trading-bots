python3 -c "
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv('/home/ubuntu/.bashrc_custom')
APCA_BASE_URL = os.getenv("APCA_PAPER_URL", "https://paper-api.alpaca.markets")

orders = api.list_orders(status='open')
for order in orders:
    print(f'⏳ Open Order: {order.symbol} | {order.side} | {order.qty} shares at {order.limit_price if order.limit_price else 'Market'}')
"
