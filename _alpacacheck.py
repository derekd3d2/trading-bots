python3 -c "
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv('/home/ubuntu/.bashrc_custom')
api = tradeapi.REST(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'), 'https://paper-api.alpaca.markets', api_version='v2')

orders = api.list_orders(status='open')
for order in orders:
    print(f'⏳ Open Order: {order.symbol} | {order.side} | {order.qty} shares at {order.limit_price if order.limit_price else 'Market'}')
"
