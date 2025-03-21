import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import pandas as pd
import os

# Setup Alpaca API
api = tradeapi.REST(
    os.getenv('APCA_API_KEY_ID'),
    os.getenv('APCA_API_SECRET_KEY'),
    base_url='https://paper-api.alpaca.markets'
)

today = datetime.now().date()
orders = api.list_orders(status='all', after=pd.Timestamp(today).strftime('%Y-%m-%dT%H:%M:%SZ'), direction='asc')

buy_total = 0.0
sell_total = 0.0
buy_prices = {}

for order in orders:
    filled_qty = float(order.filled_qty)
    avg_price = float(order.filled_avg_price)

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

    elif order.side == 'sell':
        sell_total += filled_qty * avg_price

# Get current market value at end-of-day prices
market_close = datetime.now().replace(hour=15, minute=59)
stock_value_end_of_day = 0.0
for symbol, data in buy_prices.items():
    bars = api.get_bars(symbol, timeframe='1Min', start=market_close.isoformat(), limit=1).df
    if not bars.empty:
        closing_price = bars.iloc[-1]['close']
        current_value = data['qty'] * closing_price
        buy_prices[symbol]['closing_price'] = closing_price
        stock_value_end_of_day += current_value
    else:
        print(f"⚠️ No market data available for {symbol}")
        buy_prices[symbol]['closing_price'] = None

net_profit_loss = sell_total + stock_value_end_of_day - buy_total

# Summary Display
print("\n========== Daily Trade Summary ==========")
print(f"Total Spent (Buys): ${buy_total:.2f}")
print(f"Total Earned (Sells): ${sell_total:.2f}")
print(f"End of Day Stock Value (Today's Buys): ${stock_value_end_of_day:.2f}")
print(f"Net Profit/Loss: ${net_profit_loss:.2f}")

print("\n--- Today's Stocks Summary ---")
for symbol, data in buy_prices.items():
    if data['closing_price']:
        gain_loss = (data['closing_price'] - data['total_spent']/data['qty']) * data['qty']
        status = "🔼" if gain_loss >= 0 else "🔽"
        print(f"{symbol}: Bought at ${data['total_spent']/data['qty']:.2f}, "
              f"End of Day ${data['closing_price']:.2f}, "
              f"{status} ${gain_loss:.2f}")
    else:
        print(f"{symbol}: Bought at ${data['total_spent']/data['qty']:.2f}, No end-of-day price available.")
