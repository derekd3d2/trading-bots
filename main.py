import subprocess
import time
from datetime import datetime
import pytz

def log(message):
    log_file = "/home/ubuntu/trading-bots/main.log"
    try:
        with open(log_file, "a") as f:
            f.write(f"{datetime.now()} - {message}\n")
    except Exception as e:
        print(f"⚠️ Log write failed: {e}")

# ✅ Function to sync system time
def sync_system_time():
    try:
        subprocess.run(["sudo", "timedatectl", "set-ntp", "true"], check=True)
        log("✅ System time synchronized.")
    except Exception as e:
        log(f"❌ Time sync failed: {e}")

# ✅ Start Day Trading Bot
def start_day_trading_bot():
    try:
        subprocess.Popen(["nohup", "python3", "/home/ubuntu/trading-bots/day_trading_bot.py", "&"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("🚀 Day trading bot started.")
    except Exception as e:
        log(f"❌ Failed to start day trading bot: {e}")

# ✅ Start AI Auto-Update
def start_ai_auto_update():
    try:
        subprocess.Popen(["nohup", "python3", "/home/ubuntu/trading-bots/ai_auto_update.py", "&"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("🔄 AI Auto-update started.")
    except Exception as e:
        log(f"❌ Failed to start AI auto-update: {e}")

# ✅ Main Execution
if __name__ == "__main__":
    sync_system_time()

    # Convert to Eastern Time (ET)
    et = pytz.timezone("America/New_York")
    now_et = datetime.now(et)
    market_open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    log(f"📅 Market open set for {market_open_time}")

    while datetime.now(et) < market_open_time:
        log("🕑 Waiting for market to open...")
        time.sleep(30)

    start_day_trading_bot()
    start_ai_auto_update()

    log("✅ Main execution complete.")
