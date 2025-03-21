from dotenv import load_dotenv
import subprocess
import time
from datetime import datetime
import pytz
import alpaca_trade_api as tradeapi
import json
import os

# ✅ Define log function FIRST
def log(message):
    log_file = "/home/ubuntu/trading-bots/main.log"
    try:
        with open(log_file, "a") as f:
            f.write(f"{datetime.now()} - {message}\n")
    except Exception as e:
        print(f"⚠️ Log write failed: {e}")

# ✅ Load API Key from Environment
api_key = os.getenv("QUIVER_API_KEY")

if not api_key:
    # Fallback: Load from .bashrc_custom
    load_dotenv("/home/ubuntu/.bashrc_custom")
    api_key = os.getenv("QUIVER_API_KEY")

if not api_key:
    raise ValueError("❌ API Key not found! Make sure it is set in the environment.")

log(f"✅ API Key successfully loaded in ms_congress.py")

# ✅ Load Congress Trading Data
def load_congress_trades():
    try:
        with open("/home/ubuntu/trading-bots/congress_signals.json", "r") as file:
            congress_data = json.load(file)
        return {trade["ticker"]: trade.get("congress_score", 0) for trade in congress_data}
    except FileNotFoundError:
        log("❌ Congress trading data not found.")
        return {}

# ✅ Main Execution
if __name__ == "__main__":
    congress_trades = load_congress_trades()
    print(f"✅ {len(congress_trades)} trade signals saved to congress_signals.json")


# ✅ Load Day Trading Signals
def load_trade_signals():
    try:
        with open("/home/ubuntu/trading-bots/day_trading_signals.json", "r") as file:
            signals = json.load(file)
        return signals
    except FileNotFoundError:
        log("❌ No day trading signals file found.")
        return []

# ✅ Select Best 10-15 Stocks from Signals
def filter_top_stocks():
    signals = load_trade_signals()
    congress_scores = load_congress_trades()

    for stock in signals:
        ticker = stock["ticker"]
        stock["congress_score"] = congress_scores.get(ticker, 0)  # Default to 0 if not found
        stock["total_score"] = (
            (stock["congress_score"] * 0.4) +  # 40% Weight: Congress trades
            (stock.get("insider_score", 0) * 0.3) + (stock.get("ai_score", 0) * 0.2) +   # 30% Weight: Insider buying or AI score fallback
            (stock.get("ai_score", 0) * 0.2) +  # 20% Weight: AI Sentiment
            (stock.get("momentum_score", 0) * 0.05) +  # 5% Weight: Stock momentum
            (stock.get("volume_score", 0) * 0.05)      # 5% Weight: Trading volume
        )

    # Sort by highest AI score
    sorted_stocks = sorted(signals, key=lambda x: x['total_score'], reverse=True)

    # Select top 10-15 stocks
    selected_stocks = sorted_stocks[:15]

    with open("/home/ubuntu/trading-bots/day_trading_signals.json", "w") as file:
        json.dump(selected_stocks, file, indent=4)
    
    log(f"✅ Selected {len(selected_stocks)} high-confidence trades for today.")
    return selected_stocks

# ✅ Main Execution
if __name__ == "__main__":
    # Convert to Eastern Time (ET)
    et = pytz.timezone("America/New_York")
    now_et = datetime.now(et)
    market_open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    log(f"📅 Market open set for {market_open_time}")

    selected_stocks = filter_top_stocks()
    if selected_stocks:
        log("🚀 High-confidence trades selected and ready for execution.")
