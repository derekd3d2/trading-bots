import subprocess
import time
from datetime import datetime
import pytz
import alpaca_trade_api as tradeapi
import json
import os

def log(message):
    log_file = "/home/ubuntu/trading-bots/main.log"
    try:
        with open(log_file, "a") as f:
            f.write(f"{datetime.now()} - {message}\n")
    except Exception as e:
        print(f"⚠️ Log write failed: {e}")

# ✅ Load Congress Trading Data
def load_congress_trades():
    try:
        with open("/home/ubuntu/trading-bots/congress_signals.json", "r") as file:
            congress_data = json.load(file)
        return {trade["ticker"]: trade.get("congress_score", 0) for trade in congress_data}
    except FileNotFoundError:
        log("❌ Congress trading data not found.")
        return {}

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
            (stock.get("insider_score", 0) * 0.3) +   # 30% Weight: Insider buying
            (stock.get("momentum_score", 0) * 0.1) +  # 10% Weight: Stock momentum
            (stock.get("sentiment_score", 0) * 0.1) +  # 10% Weight: WSB/Twitter sentiment
            (stock.get("volume_score", 0) * 0.1)      # 10% Weight: Trading volume
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
