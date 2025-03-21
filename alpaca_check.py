import alpaca_trade_api as tradeapi

# 🔑 Replace with your actual Alpaca API keys
ALPACA_API_KEY = "PKEBHGQHMD3E99AF6F2D"  # Your API Key
ALPACA_SECRET_KEY = "UJ6FHeoQeyfQspeSv5Zl45UFyAUTfPQJ7snvrcWy"  # Your Secret Key
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"  # Change to "https://api.alpaca.markets" for live trading

# Initialize Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version='v2')

try:
    # Fetch account details
    account = api.get_account()

    # Print account status and balance
    print(f"✅ Account Status: {account.status}")
    print(f"💰 Account Balance: ${account.cash}")

    # Fetch open orders
    orders = api.list_orders(status='open')
    if orders:
        print("📋 Open Orders:")
        for order in orders:
            price = order.limit_price if order.limit_price else 'Market'
            print(f"⏳ {order.symbol} | {order.side} | {order.qty} shares at {price}")
    else:
        print("✅ No open orders.")

except tradeapi.rest.APIError as e:
    print(f"🚨 API Error: {e}")
