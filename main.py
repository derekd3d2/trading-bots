import subprocess
import time
import os

# ✅ Function to Start Trading Bot
def start_trading_bot():
    print("🚀 Starting Trading Bot...")
    subprocess.Popen(["nohup", "python3", "trading_bot.py", ">", "output.log", "2>&1", "&"], shell=False)

# ✅ Function to Start AI Auto-Update System
def start_auto_update():
    print("🔄 Starting Auto-Update System...")
    subprocess.Popen(["nohup", "python3", "botai_auto_update.py", ">", "auto_update.log", "2>&1", "&"], shell=False)

# ✅ Function to Monitor and Restart if Needed
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
    
    # ✅ Start both components
    start_trading_bot()
    start_auto_update()
    
    # ✅ Monitor and restart if needed
    monitor_processes()
