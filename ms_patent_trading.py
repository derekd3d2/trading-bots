import os
import requests
import sqlite3
import json
from datetime import datetime, timedelta
import yfinance as yf

# ✅ Load QuiverQuant API Key
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")
if not QUIVER_API_KEY:
    print("❌ API Key not found! Make sure it is set correctly.")
    exit(1)

# ✅ QuiverQuant Patent API Endpoint
PATENTS_API_URL = "https://api.quiverquant.com/beta/live/allpatents"

# ✅ Centralized Trades Database
TRADE_DB_FILE = "trades.db"
trade_conn = sqlite3.connect(TRADE_DB_FILE)
trade_cursor = trade_conn.cursor()

# ✅ SQLite Database Connection for Patents (read-only, no creation)
DB_FILE = "patent_trading.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# ✅ Strategy Parameters
CLAIMS_THRESHOLD = 20
RECENT_DAYS = 30
SCORE_THRESHOLD = 20
STRONG_PICKS = {"QCOM", "AMD", "NVDA", "SNOW", "PLTR"}

# ✅ Helper Functions for Additional Criteria

def check_financial_health(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('returnOnEquity', 0) > 0.15 and info.get('earningsGrowth', 0) > 0.1
    except:
        return False

def check_technical_analysis(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")
        return hist['Close'].iloc[-1] > hist['Close'].iloc[-20:].mean()
    except:
        return False

def check_industry_trends(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        return hist['Close'].iloc[-1] > hist['Close'].iloc[0]
    except:
        return False

# ✅ Check Recent Purchases in Centralized DB

def recently_bought(ticker, days, strategy):
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
    trade_cursor.execute("""
        SELECT buy_date FROM trades
        WHERE ticker=? AND buy_date>=? AND bot_strategy=? AND status='OPEN'
    """, (ticker, cutoff_date, strategy))
    return trade_cursor.fetchone() is not None

# ✅ Fetch and Score Patents (without inserting into the database)

def fetch_and_score_patents():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    response = requests.get(PATENTS_API_URL, headers=headers)
    response.raise_for_status()
    patents = response.json()

    patent_scores = {}
    recent_cutoff_date = (datetime.utcnow() - timedelta(days=RECENT_DAYS)).strftime('%Y-%m-%d')

    for patent in patents:
        ticker = patent["Ticker"]
        claims = patent["Claims"]
        publication_date = patent["Date"]

        score = 0
        if claims >= CLAIMS_THRESHOLD:
            score += 4
        if publication_date >= recent_cutoff_date:
            score += 4

        if ticker not in patent_scores:
            patent_scores[ticker] = 0
        patent_scores[ticker] += score

    ticker_counts = {}
    for patent in patents:
        ticker = patent["Ticker"]
        publication_date = patent["Date"]
        if publication_date >= recent_cutoff_date:
            ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

    for ticker, count in ticker_counts.items():
        if count >= 2:
            patent_scores[ticker] += 3

    qualified_tickers = {}
    for ticker in patent_scores.keys():
        total_score = patent_scores[ticker]

        if check_technical_analysis(ticker):
            total_score += 3
        if check_industry_trends(ticker):
            total_score += 2
        if check_financial_health(ticker):
            total_score += 1

        try:
            stock = yf.Ticker(ticker)
            price_data = stock.history(period="1d")
            if price_data.empty:
                print(f"No price data available for {ticker}, skipping.")
                continue
            price = price_data['Close'].iloc[-1]
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            continue

        if ticker in STRONG_PICKS or (ticker not in STRONG_PICKS and price < 25):
            if not recently_bought(ticker, 30, "LONG") or (recently_bought(ticker, 60, "LONG") and not recently_bought(ticker, 30, "LONG")):
                if total_score >= SCORE_THRESHOLD:
                    qualified_tickers[ticker] = total_score

    return qualified_tickers

# ✅ Save Patent trading signals (market research only, no trade insertion)

def save_signals(tickers_scores, filename="patent_signals.json"):
    trade_signals = []
    for ticker, score in tickers_scores.items():
        trade_signals.append({"ticker": ticker, "ai_score": score, "action": "BUY", "strategy": "LONG"})

    with open(filename, "w") as f:
        json.dump(trade_signals, f, indent=4)
    print(f"✅ {len(trade_signals)} Patent trading signals saved to {filename}")

# ✅ Main execution
if __name__ == "__main__":
    print("🔬 Running Long-Term Patent Market Research...")
    patent_tickers_scores = fetch_and_score_patents()
    save_signals(patent_tickers_scores)
