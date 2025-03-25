from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce

# 🔑 Your real LIVE API keys
API_KEY = "AKWQTTXXDSY7FJG6AR6E"
SECRET_KEY = "Y67fyhzaohIM7dB4kjxemqwKp6MyPvfEthUdHNa0"

# 🛒 Option contract you want to buy
OPTION_SYMBOL = "IONQ250328C00023500"

# ⚙️ Setup client (set paper=False for live trading)
trade_client = TradingClient(API_KEY, SECRET_KEY, paper=False)

# 🧾 Create and send market order
order = MarketOrderRequest(
    symbol=OPTION_SYMBOL,
    qty=1,
    side=OrderSide.BUY,
    type=OrderType.MARKET,
    time_in_force=TimeInForce.DAY
)

# 🚀 Submit the order and print result
response = trade_client.submit_order(order)
print("✅ ORDER SUBMITTED:")
print(response)
