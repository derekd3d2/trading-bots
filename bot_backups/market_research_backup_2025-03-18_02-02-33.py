import os
import requests
import sqlite3
import yfinance as yf
from datetime import datetime

# ✅ Load API Key
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

# ✅ QuiverQuant API Endpoints
CONGRESS_API_URL = "https://api.quiverquant.com/beta/live/congresstrading"
INSIDER_API_URL = "https://api.quiverquant.com/beta/live/insider"
PATENTS_API_URL = "https://api.quiverquant.com/beta/live/allpatents"

# ✅ Setup SQLite Database
DB_FILE = "market_research.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# ✅ Create Tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS congress_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    trade_type TEXT,
    congress_member TEXT,
    amount TEXT,
    transaction_date TEXT,
    report_date TEXT,
    buy_price REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS insider_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    trade_type TEXT,
    insider_name TEXT,
    shares INTEGER,
    share_price REAL,
    transaction_date TEXT,
    filing_date TEXT,
    total_value REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS patents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    patent_number TEXT,
    title TEXT,
    ipc_code TEXT,
    claims INTEGER,
    abstract TEXT,
    publication_date TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ✅ Fetch & Store Congress Trading Data
def fetch_congress_trades():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    try:
        response = requests.get(CONGRESS_API_URL, headers=headers)
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return

        trades = response.json()
        if not trades:
            print("⚠️ No data received from QuiverQuant API.")
            return

        for trade in trades:
            ticker = trade["Ticker"]
            latest_price = get_stock_price(ticker)
            if latest_price is None:
                continue  

            cursor.execute("""
                INSERT INTO congress_trades (ticker, trade_type, congress_member, amount, transaction_date, report_date, buy_price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ticker, trade["Transaction"], trade["Representative"], trade["Amount"], trade["TransactionDate"], trade["ReportDate"], latest_price))
        conn.commit()
        print("✅ Congress trading data updated.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error while fetching Congress trades: {e}")

# ✅ Fetch & Store Insider Trading Data
def fetch_insider_trades():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    try:
        response = requests.get(INSIDER_API_URL, headers=headers)
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return

        trades = response.json()
        if not trades:
            print("⚠️ No data received from QuiverQuant API.")
            return

        for trade in trades:
            cursor.execute("""
                INSERT INTO insider_trades (ticker, trade_type, insider_name, shares, share_price, transaction_date, filing_date, total_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (trade["Ticker"], trade["Transaction"], trade["Name"], trade["Shares"], trade["SharePrice"], trade["TransactionDate"], trade["FilingDate"], trade["TotalValue"]))
        conn.commit()
        print("✅ Insider trading data updated.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error while fetching Insider trades: {e}")

# ✅ Fetch & Store Patent Data
def fetch_patents():
    headers = {"accept": "application/json", "Authorization": f"Bearer {QUIVER_API_KEY}"}
    try:
        response = requests.get(PATENTS_API_URL, headers=headers)
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return

        patents = response.json()
        if not patents:
            print("⚠️ No data received from QuiverQuant API.")
            return

        for patent in patents:
            cursor.execute("""
                INSERT INTO patents (ticker, patent_number, title, ipc_code, claims, abstract, publication_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (patent["Ticker"], patent["PatentNumber"], patent["Title"], patent["IPC"], patent["Claims"], patent["Abstract"], patent["Date"]))
        conn.commit()
        print("✅ Patent data updated.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error while fetching Patent data: {e}")

# ✅ Get Stock Price from Yahoo Finance with Error Handling
def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="5d")
        if history.empty:
            return None
        latest_price = history["Close"].dropna().iloc[-1]
        return latest_price
    except Exception as e:
        return None

if __name__ == "__main__":
    fetch_congress_trades()
    fetch_insider_trades()
    fetch_patents()
