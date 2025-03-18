import subprocess
import time
import os
from datetime import datetime
import pytz

# ✅ Function to Wait Until Market Open (9:30 AM EST)
def wait_until_market_open():
    """Pause the script until the market opens at 9:30 AM EST."""
    est = pytz.timezone('America/New_York')
    while True:
        now = datetime.now(est)
        print(f"🔎 DEBUG: Current time in EST: {now.strftime('%Y-%m-%d %H:%M:%S EST')}")
        
        if now.hour >= 9 and now.minute >= 30:
            print("🚀 Market is open! Starting trading scripts...")
            break

        print(f"⏳ Waiting for market open... Current time: {now.strftime('%Y-%m-%d %H:%M:%S EST')}")
        time.sleep(60)  # Check every 60 seconds

# ✅ Function to Start Market Research Bot (Fetch Congress Trades)
def start_market_research():
    print("📊 Starting Market Research Bot (Fetching Congress Trades)...")
    subprocess.run(["python3", "market_research.py"])

# ✅ Function to Start Trading Bot (Execute Trades)
def start_trading_bot():
    print("🚀 Starting Trading Bot...")
    subprocess.Popen(["nohup", "python3", "trading_bot.py", ">", "output.log", "2>&1", "&"], shell=False)

# ✅ Function to Start AI Auto-Update System
def start_auto_update():
    print("🔄 Starting Auto-Update System...")
    subprocess.Popen(["nohup", "python3", "botai_auto_update.py", ">", "auto_update.log", "2>&1", "&"], shell=False)

# ✅ Function to Monitor and Restart Processes If Needed
def monitor_processes():
    while True:
        time.sleep(3600)  # Check every hour

        # Check if Trading Bot is running
        bot_running = subprocess.run(["pgrep", "-f", "trading_bot.py"], capture_output=True, text=True).stdout.strip()
        if not bot_running:
            print("❌ Trading Bot stopped! Restarting...")
            start_trading_bot()

        # Check if Auto-Update System is running
        auto_update_running = subprocess.run(["pgrep", "-f", "botai_auto_update.py"], capture_output=True, text=True).stdout.strip()
        if not auto_update_running:
            print("❌ Auto-Update System stopped! Restarting...")
            start_auto_update()

if __name__ == "__main__":
    print("🚀 Starting AI Trading System...")

    # ✅ Wait until the stock market opens at 9:30 AM EST
    wait_until_market_open()

    # ✅ Start Market Research Bot First
    start_market_research()

    # ✅ Wait 15 minutes before starting Trading Bot (to ensure signals are updated)
    time.sleep(900)
    
    # ✅ Start Trading Bot
    start_trading_bot()

    # ✅ Start Auto-Update System
    start_auto_update()

    # ✅ Monitor and restart if needed
    monitor_processes()

