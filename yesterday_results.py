import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import pandas as pd
import os

# Setup Alpaca API
api = tradeapi.REST(
    os.getenv('APCA_API_KEY_ID'),
    os.getenv('APCA_API_SECRET_KEY'),
APCA_BASE_URL = os.getenv("APCA_PAPER_URL", "https://paper-api.alpaca.markets")
)

# Calculate yesterday's market date range (using UTC time)
yesterday = datetime.utcnow() - timedelta(days=1)
market_open = yesterday.replace(hour=13, minute=30, second=0, microsecond=0)  # 9:30 AM ET
market_close = yesterday.replace(hour=20, minute=0, second=0, microsecond=0)  # 4:00 PM ET

after = market_open.strftime('%Y-%m-%dT%H:%M:%SZ')
until = market_close.strftime('%Y-%m-%dT%H:%M:%SZ')

# Fetch yesterday's completed orders
orders = api.list_orders(status='filled', after=after, until=until, direction='asc')

buy_total, sell_total = 0.0, 0.0
buy_prices = {}
sell_prices = {}
realized_profit_loss = 0.0

for order in orders:
    try:
        if order.filled_qty and order.filled_avg_price:
            filled_qty = float(order.filled_qty)
            avg_price = float(order.filled_avg_price)

            if order.side == 'buy':
                buy_total += filled_qty * avg_price
                if order.symbol in buy_prices:
                    buy_prices[order.symbol]['qty'] += filled_qty
                    buy_prices[order.symbol]['total_spent'] += filled_qty * avg_price
                else:
                    buy_prices[order.symbol] = {'qty': filled_qty, 'total_spent': filled_qty * avg_price}

            elif order.side == 'sell':
                sell_total += filled_qty * avg_price
                if order.symbol in buy_prices:
                    avg_entry_price = buy_prices[order.symbol]['total_spent'] / buy_prices[order.symbol]['qty']
                    realized_profit_loss += (avg_price - avg_entry_price) * filled_qty
                    
                sell_prices[order.symbol] = {'qty': filled_qty, 'sell_price': avg_price}
    except Exception as e:
        print(f"⚠️ Error processing order {order.id}: {e}")

# Get latest market closing prices
unrealized_profit_loss = 0.0
for symbol, data in buy_prices.items():
    try:
        latest_bar = api.get_latest_bar(symbol)
        closing_price = latest_bar.c if latest_bar else None

        if closing_price:
            buy_prices[symbol]['closing_price'] = closing_price
            unrealized_gain_loss = (closing_price - data['total_spent'] / data['qty']) * data['qty']
            unrealized_profit_loss += unrealized_gain_loss
        else:
            print(f"⚠️ No closing data for {symbol}")
            buy_prices[symbol]['closing_price'] = None
    except Exception as e:
        print(f"⚠️ Error fetching latest price for {symbol}: {e}")

# Calculate net profit/loss correctly
net_profit_loss = realized_profit_loss + unrealized_profit_loss

# Summary Display
print("\n========== Daily Trade Summary ==========")
print(f"Total Spent (Buys): ${buy_total:.2f}")
print(f"Total Earned (Sells): ${sell_total:.2f}")
print(f"Realized Profit/Loss (Sells): ${realized_profit_loss:.2f}")
print(f"Unrealized Profit/Loss (Today's Buys): ${unrealized_profit_loss:.2f}")
print(f"Net Profit/Loss: ${net_profit_loss:.2f}")

print("\n--- Today's Stocks Summary ---")
for symbol, data in buy_prices.items():
    if data['closing_price']:
        gain_loss = (data['closing_price'] - data['total_spent'] / data['qty']) * data['qty']
        status = "🔼" if gain_loss >= 0 else "🔽"
        print(f"{symbol}: Bought at ${data['total_spent']/data['qty']:.2f}, "
              f"End of Day ${data['closing_price']:.2f}, "
              f"{status} ${gain_loss:.2f}")
    else:
        print(f"{symbol}: Bought at ${data['total_spent']/data['qty']:.2f}, No end-of-day price available.")
