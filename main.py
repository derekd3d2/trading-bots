import subprocess
import time
from datetime import datetime
import pytz
import os

def log(message):
    log_file = "/home/ubuntu/trading-bots/main.log"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"{timestamp} - {message}"
    print(log_message)  # Show live in terminal
    try:
        with open(log_file, "a") as f:
            f.write(log_message + "\n")
    except Exception as e:
        print(f"⚠️ Log write failed: {e}")

# ✅ Run subprocess and log output
def run_bot(script_path, name):
    log(f"📥 Starting {name}...")
    try:
        result = subprocess.run(["python3", script_path], capture_output=True, text=True)
        log(f"✅ {name} completed.")
        if result.stdout:
            log(f"📤 {name} stdout:\n{result.stdout.strip()}")
        if result.stderr:
            log(f"⚠️ {name} stderr:\n{result.stderr.strip()}")
    except Exception as e:
        log(f"❌ {name} failed: {e}")

# ✅ Main Execution
if __name__ == "__main__":
    log("🚀 main.py started.")

    # Log ET time
    et = pytz.timezone("America/New_York")
    now_et = datetime.now(et)
    log(f"🕒 Current Eastern Time: {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    market_open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    # ✅ Wait until market opens at 9:30 AM ET
    while now_et < market_open_time:
        print(f"⏳ Waiting for market to open... Current ET: {now_et.strftime('%H:%M:%S')}")
        time.sleep(30)
        now_et = datetime.now(et)

    # ✅ ML Prediction Step
    if os.path.exists("/home/ubuntu/trading-bots/day_trade_model.pkl"):
        run_bot("/home/ubuntu/trading-bots/predict_day_trades.py", "Predict Day Trades")
    else:
        log("⚠️ ML model not found. Skipping prediction and using raw signals.")

    # ✅ Day Trading
    run_bot("/home/ubuntu/trading-bots/day_trading_bot.py", "Day Trading Bot")

    # ✅ Short Trading
    run_bot("/home/ubuntu/trading-bots/short_trading_bot.py", "Short Trading Bot")

    # ✅ AI Update
    run_bot("/home/ubuntu/trading-bots/ai_auto_update.py", "AI Auto-Update")

    log("✅ All tasks complete. main.py finished.\n")
