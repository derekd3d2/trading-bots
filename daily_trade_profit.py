import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

# Load API keys from environment
load_dotenv('/home/ubuntu/.bashrc_custom')
api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_SECRET_KEY'),
    base_url='https://paper-api.alpaca.markets'
)

# Get today's date in correct format
today = datetime.now().date()
today_iso = pd.Timestamp.today().isoformat() + "Z"  # Ensure correct ISO format

try:
    orders = api.list_orders(status='all', after=today_iso, direction='asc')
except tradeapi.rest.APIError as e:
    print(f"❌ API Error retrieving orders: {e}")
    orders = []
except Exception as e:
    print(f"❌ Unexpected error retrieving orders: {e}")
    orders = []

buy_total = 0.0
sell_total = 0.0
buy_prices = {}
holding_stocks = {}
beginning_balance = 0.0
ending_balance = 0.0

try:
    account = api.get_account()
    beginning_balance = float(account.cash) + float(account.portfolio_value)  # Capture starting balance
except tradeapi.rest.APIError as e:
    print(f"⚠️ API Error retrieving account balance: {e}")
except Exception as e:
    print(f"⚠️ Unexpected error retrieving account balance: {e}")

for order in orders:
    try:
        filled_qty = float(order.filled_qty)
        avg_price = float(order.filled_avg_price) if order.filled_avg_price is not None else 0.0
        
        if order.side == 'buy':
            buy_total += filled_qty * avg_price
            if order.symbol in buy_prices:
                buy_prices[order.symbol]['qty'] += filled_qty
                buy_prices[order.symbol]['total_spent'] += filled_qty * avg_price
            else:
                buy_prices[order.symbol] = {
                    'qty': filled_qty,
                    'total_spent': filled_qty * avg_price
                }
            # Track stocks that were bought but not yet sold
            holding_stocks[order.symbol] = {
                'qty': filled_qty,
                'avg_price': avg_price,
                'date_bought': order.submitted_at
            }
        elif order.side == 'sell':
            sell_total += filled_qty * avg_price
            if order.symbol in holding_stocks:
                del holding_stocks[order.symbol]  # Remove from holdings once sold
    except AttributeError:
        print(f"⚠️ Order {order.id} has missing attributes and was skipped.")
    except Exception as e:
        print(f"⚠️ Unexpected error processing order {order.id}: {e}")

# Fetch ending balance after trades
try:
    account = api.get_account()
    ending_balance = float(account.cash) + float(account.portfolio_value)
except tradeapi.rest.APIError as e:
    print(f"⚠️ API Error retrieving ending account balance: {e}")
except Exception as e:
    print(f"⚠️ Unexpected error retrieving ending account balance: {e}")

# Print summary results
print(f"✅ Beginning Balance: ${beginning_balance:.2f}")
print(f"✅ Total Buy Volume: ${buy_total:.2f}")
print(f"✅ Total Sell Volume: ${sell_total:.2f}")
print(f"✅ Ending Balance: ${ending_balance:.2f}")
print(f"📊 Buy Prices Per Stock: {buy_prices}")
print(f"📈 Stocks Still Held: {holding_stocks}")
