import os
import alpaca_trade_api as tradeapi
from datetime import datetime
import pytz
import json

# === Load API keys dynamically based on ALPACA_ENV ===
mode = os.getenv("ALPACA_ENV", "paper").lower()

if mode == "live":
    ALPACA_API_KEY = os.getenv("APCA_LIVE_KEY")
    ALPACA_SECRET_KEY = os.getenv("APCA_LIVE_SECRET")
    BASE_URL = os.getenv("APCA_LIVE_URL")
elif mode == "paper":
    ALPACA_API_KEY = os.getenv("APCA_PAPER_KEY")
    ALPACA_SECRET_KEY = os.getenv("APCA_PAPER_SECRET")
    BASE_URL = os.getenv("APCA_PAPER_URL")
else:
    raise ValueError("❌ Invalid ALPACA_ENV setting. Must be 'paper' or 'live'.")

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    raise ValueError("❌ Missing Alpaca API credentials. Please check ~/.bashrc_custom and reload env.")

# ✅ Connect to Alpaca
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL)

# ✅ Market Index Symbols
INDEXES = {
    "SPX": "SPY",   # S&P 500 proxy
    "DJI": "DIA",   # Dow Jones proxy
    "IXIC": "QQQ"    # Nasdaq proxy
}

THRESHOLD = 0.003  # 0.3% threshold for spike/drop

# ✅ Determine Trend

def get_market_trend():
    trend = {"bullish": 0, "bearish": 0, "neutral": 0}
    for name, symbol in INDEXES.items():
        try:
            barset = api.get_bars(symbol, tradeapi.TimeFrame.Minute, limit=5)
            bars = list(barset)
            if len(bars) < 2:
                print(f"⚠️ Not enough bars for {symbol}. Skipping.")
                continue
            open_price = bars[0].o
            current_price = bars[-1].c
            change = (current_price - open_price) / open_price

            if change >= THRESHOLD:
                trend['bullish'] += 1
            elif change <= -THRESHOLD:
                trend['bearish'] += 1
            else:
                trend['neutral'] += 1
        except Exception as e:
            print(f"Error getting data for {name}: {e}")

    # Decide market state
    if trend['bullish'] >= 2:
        return "bullish"
    elif trend['bearish'] >= 2:
        return "bearish"
    else:
        return "neutral"

# ✅ Save sentiment to file

def save_sentiment():
    sentiment = get_market_trend()
    with open("market_sentiment.json", "w") as f:
        f.write(f'{{"sentiment": "{sentiment}"}}')
    print(f"📊 Market sentiment: {sentiment}")

if __name__ == '__main__':
    save_sentiment()
