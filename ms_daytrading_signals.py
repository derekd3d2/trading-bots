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

# ✅ Normalize scores to 0-10 range
def normalize(score, cap=10):
    try:
        return min(float(score), cap)
    except:
        return 0

# ✅ Load Congress Trading Data
def load_congress_trades():
    try:
        with open("congress_signals.json") as f:
            data = json.load(f)

        if isinstance(data, list):
            entries = data
        else:
            entries = data.get("buy_signals", [])
        return {
            entry["ticker"]: entry.get("congress_score", 0)
            for entry in entries
            if "ticker" in entry
        }

    except FileNotFoundError:
        log("❌ Congress trading data not found.")
        return {}

# ✅ Load Insider Trading Data
def load_insider_trades():
    try:
        with open("/home/ubuntu/trading-bots/ms_insider_signals.json", "r") as file:
            data = json.load(file)
            return {entry["ticker"]: entry.get("insider_score", 0) for entry in data.get("buy_signals", [])}
    except FileNotFoundError:
        log("❌ Insider trading data not found.")
        return {}

# ✅ Load WSB Sentiment Data
def load_wsb_trades():
    try:
        with open("/home/ubuntu/trading-bots/ms_wsb_signals.json", "r") as file:
            data = json.load(file)
            return {entry["ticker"]: entry.get("wsb_score", 0) for entry in data.get("buy_signals", [])}
    except FileNotFoundError:
        log("❌ WSB sentiment data not found.")
        return {}

# ✅ Load Base Day Trading Signals
def load_trade_signals():
    try:
        with open("/home/ubuntu/trading-bots/day_trading_signals.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        log("❌ No day trading signals file found.")
        return []

# ✅ Select Top 30 High-Confidence Stocks
def filter_top_stocks():
    base_signals = load_trade_signals()
    congress_scores = load_congress_trades()
    insider_scores = load_insider_trades()
    wsb_scores = load_wsb_trades()

    all_tickers = set([s.get("ticker") for s in base_signals if s.get("ticker")])
    all_tickers.update(congress_scores.keys(), insider_scores.keys(), wsb_scores.keys())

    full_signals = []

    for ticker in all_tickers:
        if not ticker or ticker == "N/A" or "#" in ticker or not isinstance(ticker, str) or not ticker.isalnum():
            continue

        base = next((s for s in base_signals if s.get("ticker") == ticker), {})
        congress = normalize(congress_scores.get(ticker, 0))
        insider = normalize(insider_scores.get(ticker, 0))
        wsb = normalize(wsb_scores.get(ticker, 0))

        momentum = base.get("momentum_score", 0)
        volume = base.get("volume_score", 0)

        total = (
            (congress * 0.3) +
            (insider * 0.3) +
            (wsb * 0.2) +
            (momentum * 0.1) +
            (volume * 0.1)
        )

        if total < 1.0:
            continue

        print(f"🧠 {ticker}: Congress={congress}, Insider={insider}, WSB={wsb}, Momentum={momentum}, Volume={volume} → Total={round(total, 2)}")

        full_signals.append({
            "ticker": ticker,
            "congress_score": congress,
            "insider_score": insider,
            "sentiment_score": wsb,
            "momentum_score": momentum,
            "volume_score": volume,
            "total_score": total
        })

    sorted_stocks = sorted(full_signals, key=lambda x: x['total_score'], reverse=True)
    selected_stocks = sorted_stocks[:30]

    with open("/home/ubuntu/trading-bots/day_trading_signals.json", "w") as file:
        json.dump(selected_stocks, file, indent=4)

    log(f"✅ Selected {len(selected_stocks)} high-confidence trades for today.")
    return selected_stocks

# ✅ Main Execution
if __name__ == "__main__":
    et = pytz.timezone("America/New_York")
    now_et = datetime.now(et)
    market_open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    log(f"📅 Market open set for {market_open_time}")

    selected_stocks = filter_top_stocks()
    if selected_stocks:
        log("🚀 High-confidence trades selected and ready for execution.")
