import alpaca_trade_api as tradeapi
import time
from datetime import datetime, timedelta
import pytz
import os

# ENV-based Live Trading
ALPACA_KEY = os.getenv("APCA_LIVE_KEY")
ALPACA_SECRET = os.getenv("APCA_LIVE_SECRET")
BASE_URL = os.getenv("APCA_LIVE_URL")
api = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, BASE_URL, api_version='v2')

symbol = "TSLA"
quantity = 1
profit_target_pct = 0.02  # 2% gain
stop_loss_pct = 0.03      # 3% loss

def wait_until_market_open():
    clock = api.get_clock()
    if not clock.is_open:
        open_time = clock.next_open.replace(tzinfo=pytz.UTC)
        now = datetime.now(tz=pytz.UTC)
        wait_sec = (open_time - now).total_seconds()
        print(f"Market opens in {wait_sec / 60:.2f} min. Waiting...")
        time.sleep(max(wait_sec, 0))

def short_sell():
    print(f"[{datetime.now()}] Shorting {symbol}...")
    api.submit_order(
        symbol=symbol,
        qty=quantity,
        side='sell',
        type='market',
        time_in_force='day'
    )
    time.sleep(2)

def get_prices():
    position = api.get_position(symbol)
    entry = float(position.avg_entry_price)
    current = float(api.get_latest_trade(symbol).p)
    return entry, current

def check_and_exit():
    entry, current = get_prices()
    target = entry * (1 - profit_target_pct)
    stop = entry * (1 + stop_loss_pct)

    print(f"[{datetime.now()}] Entry: ${entry:.2f}, Current: ${current:.2f} | Target: ${target:.2f}, Stop: ${stop:.2f}")

    if current <= target:
        print("Profit hit. Closing position...")
        api.submit_order(symbol=symbol, qty=quantity, side='buy', type='market', time_in_force='day')
        return True
    elif current >= stop:
        print("Stop-loss hit. Closing position...")
        api.submit_order(symbol=symbol, qty=quantity, side='buy', type='market', time_in_force='day')
        return True
    return False

def in_position():
    try:
        pos = api.get_position(symbol)
        return abs(int(pos.qty)) > 0
    except:
        return False

def market_open_now():
    clock = api.get_clock()
    return clock.is_open

if __name__ == "__main__":
    wait_until_market_open()
    print("Market is open.")
    
    while market_open_now():
        if not in_position():
            short_sell()

        time.sleep(10)
        if in_position() and check_and_exit():
            print("Position closed. Waiting 5 minutes to re-enter...")
            time.sleep(300)
        else:
            print("Still holding. Checking again in 5 minutes...")
            time.sleep(300)
