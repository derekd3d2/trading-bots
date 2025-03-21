import yagmail
import alpaca_trade_api as tradeapi
import os
from datetime import datetime, timedelta
import pytz

# Set up Alpaca API
api = tradeapi.REST(
    os.getenv("APCA_API_KEY_ID")
    as.getenv("APCA_API_SECRET_KEY")
    "https://paper-api.alpaca.markets",
    api_version="v2"
)

# Set timezone explicitly
ny_tz = pytz.timezone("America/New_York")
now_ny = datetime.now(ny_tz)

# Define today's range
start_today_ny = now_ny.replace(hour=0, minute=0, second=0, microsecond=0)
end_today_ny = start_today_ny + timedelta(days=1)
start_today_utc = start_today_ny.astimezone(pytz.utc).isoformat()
end_today_utc = end_today_ny.astimezone(pytz.utc).isoformat()

# Fetch today's orders
orders = api.list_orders(status='all', after=start_today_utc, until=end_today_utc, limit=500)

spent_total = 0.0
sold_total = 0.0

for order in orders:
    if order.status == 'filled':
        filled_qty = float(order.filled_qty)
        filled_price = float(order.filled_avg_price)
        total_trade_value = filled_qty * filled_price

        if order.side == 'buy':
            spent_total += total_trade_value
        elif order.side == 'sell':
            sold_total += total_trade_value

net_profit = sold_total - spent_total

# Prepare email content clearly
subject = f"📊 Daily Trading Summary for {now_ny.strftime('%Y-%m-%d')}"
content = f"""
Daily Trading Summary ({now_ny.strftime('%Y-%m-%d')})

Total Spent (Buys): ${spent_total:.2f}
Total Earned (Sells): ${sold_total:.2f}
Net Profit/Loss: ${net_profit:.2f}
"""

# Email sender details (replace clearly)
sender_email = "derekd3d2@gmail.com"
receiver_email = "derekd3d2@Gmail.com"
email_password = os.getenv('EMAIL_PASSWORD')

# Send email explicitly
yag = yagmail.SMTP(sender_email, email_password)
yag.send(to=receiver_email, subject=subject, contents=content)

print("✅ Trading summary email sent successfully!")
