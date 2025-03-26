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


# ✅ Load Top Congress Traders
def load_top_congress_traders():
    try:
        with open("top_congress_traders.json") as f:
            return set(json.load(f))
    except FileNotFoundError:
        log("❌ Top Congress traders list not found.")
        return set()


# ✅ Load Congress Trading Data
def load_congress_trades():
    try:
        with open("congress_signals.json") as f:
            data = json.load(f)

        top_reps = load_top_congress_traders()
        entries = data.get("buy_signals", []) if isinstance(data, dict) else data

        congress_scores = {}
        for entry in entries:
            rep = entry.get("representative", "").strip()
            ticker = entry.get("ticker", "").upper()
            base_score = entry.get("congress_score", 0)
            range_str = entry.get("range", "")
            days_ago = (datetime.now() - datetime.strptime(entry.get("transaction_date", "2000-01-01"), "%Y-%m-%d")).days

            # Size-based weighting
            if "$500,001 - $1,000,000" in range_str:
                base_score += 1.5
            elif "$250,001 - $500,000" in range_str:
                base_score += 1.0
            elif "$100,001 - $250,000" in range_str:
                base_score += 0.5

            # Recency bonus
            if days_ago <= 3:
                base_score += 1

            if rep in top_reps and ticker:
                congress_scores[ticker] = congress_scores.get(ticker, 0) + base_score

        return congress_scores

    except FileNotFoundError:
        log("❌ Congress trading data not found.")
        return {}


# ✅ Load Insider Trading Data
def load_insider_trades():
    try:
        with open("/home/ubuntu/trading-bots/ms_insider_signals.json", "r") as file:
            data = json.load(file)
            return {
                entry["ticker"].upper(): entry.get("insider_score", 0)
                for entry in data.get("buy_signals", [])
                if entry.get("ticker")
            }
    except FileNotFoundError:
        log("❌ Insider trading data not found.")
        return {}


# ✅ Load WSB Sentiment Data
def load_wsb_trades():
    try:
        with open("/home/ubuntu/trading-bots/ms_wsb_signals.json", "r") as file:
            data = json.load(file)
            return {
                entry["ticker"].upper(): entry.get("wsb_score", 0)
                for entry in data.get("buy_signals", [])
                if entry.get("ticker")
            }
    except FileNotFoundError:
        log("❌ WSB sentiment data not found.")
        return {}


# ✅ LoadWSB Sentiment Gov Contracts Data
def load_gov_contracts():
    try:
        with open("/home/ubuntu/trading-bots/ms_gov_signals.json", "r") as file:
            data = json.load(file)
            return {
                entry["ticker"].upper(): entry.get("gov_score", 0)
                for entry in data.get("buy_signals", [])
                if entry.get("ticker")
            }
    except FileNotFoundError:
        log("❌ Government contract data not found.")
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
    gov_scores = load_gov_contracts()

    all_tickers = set([s.get("ticker", "").upper() for s in base_signals if s.get("ticker")])
    all_tickers.update(congress_scores.keys(), insider_scores.keys(), wsb_scores.keys(), gov_scores.keys())

    full_signals = []

    for ticker in all_tickers:
        if not ticker or ticker == "N/A" or "#" in ticker or not isinstance(ticker, str) or not ticker.isalnum():
            continue
        if len(ticker) < 2 or len(ticker) > 5:
            continue

        base = next((s for s in base_signals if s.get("ticker", "").upper() == ticker), {})
        congress = normalize(congress_scores.get(ticker, 0))
        insider = normalize(insider_scores.get(ticker, 0))
        wsb = normalize(wsb_scores.get(ticker, 0))
        gov = normalize(gov_scores.get(ticker, 0))

        total = (congress * 0.4) + (insider * 0.3) + (wsb * 0.2) + (gov * 0.1)

        if total < 1.0:
            continue

        print(f"🧐 {ticker}: Congress={congress}, Insider={insider}, WSB={wsb}, Gov={gov} → Total={round(total, 2)}")

        full_signals.append({
            "ticker": ticker,
            "congress_score": congress,
            "insider_score": insider,
            "sentiment_score": wsb,
            "gov_score": gov,
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
