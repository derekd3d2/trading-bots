import os
import alpaca_trade_api as tradeapi

# ✅ Load API Keys
APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
APCA_BASE_URL = os.getenv("APCA_PAPER_URL", "https://paper-api.alpaca.markets")

# ✅ Connect to Alpaca API
api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_BASE_URL, api_version="v2")

# ✅ Cancel All Open Orders
def cancel_all_orders():
    orders = api.list_orders(status="open")
    if not orders:
        print("✅ No open orders to cancel.")
        return

    print(f"🔍 Found {len(orders)} open orders. Cancelling all...")
    for order in orders:
        try:
            api.cancel_order(order.id)
            print(f"✅ Canceled order {order.id} for {order.symbol}")
        except Exception as e:
            print(f"❌ Error canceling order {order.id}: {e}")

    print("✅ All open orders have been canceled.")

if __name__ == "__main__":
    cancel_all_orders()
