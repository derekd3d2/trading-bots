import subprocess
import time
from datetime import datetime
import pytz
import os
import json

# ✅ Logging

def log(message):
    log_file = "/home/ubuntu/trading-bots/main.log"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"{timestamp} - {message}"
    print(log_message)
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

    et = pytz.timezone("America/New_York")
    now_et = datetime.now(et)
    log(f"🕒 Current Eastern Time: {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    # ✅ Step 1: Run Market Sentiment
    run_bot("/home/ubuntu/trading-bots/market_sentiment.py", "Market Sentiment")

    # ✅ Step 2: Read sentiment result
    sentiment_file = "/home/ubuntu/trading-bots/market_sentiment.json"
    if os.path.exists(sentiment_file):
        with open(sentiment_file, "r") as f:
            sentiment_data = json.load(f)
            sentiment = sentiment_data.get("sentiment", "neutral")
            log(f"🔍 Detected Market Sentiment: {sentiment}")
    else:
        sentiment = "neutral"
        log("⚠️ Sentiment file not found. Defaulting to NEUTRAL.")

    # ✅ Step 3: ML Prediction (optional)
    if os.path.exists("/home/ubuntu/trading-bots/day_trade_model.pkl"):
        run_bot("/home/ubuntu/trading-bots/predict_day_trades.py", "Predict Day Trades")
    else:
        log("⚠️ ML model not found. Skipping prediction and using raw signals.")

    # ✅ Step 4: Trade Based on Sentiment
    if sentiment == "bullish":
        run_bot("/home/ubuntu/trading-bots/momentum_long_bot.py", "Momentum Long Bot")
    elif sentiment == "bearish":
        run_bot("/home/ubuntu/trading-bots/momentum_short_bot.py", "Momentum Short Bot")
    else:
        run_bot("/home/ubuntu/trading-bots/momentum_long_bot.py", "Momentum Long Bot")
        run_bot("/home/ubuntu/trading-bots/momentum_short_bot.py", "Momentum Short Bot")

    # ✅ Final Step: Day Trading Execution
    run_bot("/home/ubuntu/trading-bots/day_trading_bot.py", "Day Trading Bot")

    log("✅ All tasks complete. main.py finished.\n")
