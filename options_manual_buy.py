import os
import requests
import json

# === Alpaca LIVE CREDENTIALS (replace with your actual keys) ===
ALPACA_API_KEY = "AKQLAH7WUPSEO96MNH7T"
ALPACA_SECRET = "AUzXSxevkdFAGs05xT6NzqNpG0e6bmHfiddjEY1v"

# === Headers ===
HEADERS = {
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET
}

# === Historical stock price fetch ===
def get_stock_price_history(symbol, start_date, end_date):
    BASE_URL = 'https://data.alpaca.markets/v2/stocks/bars'
    params = {
        'symbols': symbol,
        'timeframe': '1D',
        'start': start_date,
        'end': end_date,
        'limit': 1000
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data:", response.text)
        return None

# === Test call ===
symbol = "TQQQ"
start_date = "2023-01-01"
end_date = "2023-05-13"

historical_data = get_stock_price_history(symbol, start_date, end_date)

if historical_data:
    bars = historical_data.get("bars", [])
    for bar in bars:
        date = bar.get("t")
        open_price = bar.get("o")
        high_price = bar.get("h")
        low_price = bar.get("l")
        close_price = bar.get("c")
        volume = bar.get("v")

        print(f"Date: {date}")
        print(f"Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}")
        print(f"Volume: {volume}\n")
