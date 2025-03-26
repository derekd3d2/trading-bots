import requests
import os

def normalize(score, cap=10):
    try:
        return min(float(score), cap)
    except:
        return 0

API_KEY = os.getenv("QUIVER_API_KEY")
HEADERS = {"accept": "application/json", "Authorization": f"Bearer {API_KEY}"}

def fetch_congress_sells():
    url = "https://api.quiverquant.com/beta/live/congresstrading"
    data = requests.get(url, headers=HEADERS).json()
    sells = {}
    for row in data:
        if row.get("Transaction", "").lower() == "sale":
            ticker = row.get("Ticker")
            if not ticker:
                continue
            ticker = ticker.upper()
            try:
                amount = float(row.get("Amount", 0))
            except (ValueError, TypeError):
                amount = 0
            sells[ticker] = sells.get(ticker, 0) + amount / 10000
    return sells

def fetch_insider_sells():
    url = "https://api.quiverquant.com/beta/live/insiders"
    data = requests.get(url, headers=HEADERS).json()
    sells = {}
    for row in data:
        if row and row.get("AcquiredDisposedCode") == "D":
            ticker = row.get("Ticker")
            if not ticker:
                continue
            ticker = ticker.upper()
            try:
                shares = float(row.get("Shares", 0) or 0)
                price = float(row.get("PricePerShare", 0) or 0)
                value = shares * price
            except (ValueError, TypeError):
                value = 0
            sells[ticker] = sells.get(ticker, 0) + value / 10000
    return sells

def fetch_wsb_bearish():
    url = "https://api.quiverquant.com/beta/live/wallstreetbets"
    data = requests.get(url, headers=HEADERS).json()
    bearish = {}
    for row in data:
        puts = row.get("Puts", 0)
        calls = row.get("Calls", 0)
        if puts > calls:
            ticker = row.get("Ticker")
            if not ticker:
                continue
            ticker = ticker.upper()
            bearish[ticker] = bearish.get(ticker, 0) + (puts - calls)
    return bearish

def get_top_short_signals(current_positions=None, open_orders=None):
    if current_positions is None:
        current_positions = set()
    if open_orders is None:
        open_orders = set()

    skip_tickers = current_positions | open_orders

    congress = fetch_congress_sells()
    insider = fetch_insider_sells()
    wsb = fetch_wsb_bearish()
    tickers = set(congress.keys()) | set(insider.keys()) | set(wsb.keys())

    scored = []
    for ticker in tickers:
        if ticker in skip_tickers:
            continue  # Skip if already held or has pending order

        score = (
            normalize(congress.get(ticker, 0)) * 0.4 +
            normalize(insider.get(ticker, 0)) * 0.4 +
            normalize(wsb.get(ticker, 0)) * 0.2
        )
        if score >= 1.0:
            scored.append({"ticker": ticker, "short_score": round(score, 2)})

    return sorted(scored, key=lambda x: x["short_score"], reverse=True)[:3]
