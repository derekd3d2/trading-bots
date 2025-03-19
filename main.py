import subprocess
import time
from datetime import datetime

# ✅ Function to sync system time (optional)
def sync_system_time():
    subprocess.run(["sudo", "timedatectl", "set-ntp", "true"], check=True)
    print("✅ System time synchronized.")

# ✅ Start Day Trading Bot
def start_day_trading_bot():
    subprocess.Popen(["python3", "/home/ubuntu/trading-bots/day_trading_bot.py"])
    print("🚀 Day trading bot started.")

def start_ai_auto_update():
    subprocess.Popen(["python3", "/home/ubuntu/trading-bots/ai_auto_update.py"])
    print("🔄 AI Auto-update started.")

# ✅ Main Execution
if __name__ == "__main__":
    sync_system_time()

    # Confirm market open time
    market_open_time = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
    print(f"📅 Market open set for {market_open_time}")

    while datetime.now() < market_open_time:
        print("🕑 Waiting for market to open...")
        time.sleep(30)

    start_day_trading_bot()
    start_ai_auto_update()

    print("✅ Main execution complete.")
