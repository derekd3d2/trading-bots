import os
import json
import math
import time
from datetime import datetime, timedelta
from collections import Counter
import requests
import csv

OPTION_LOG_FILE = "option_trade_log.json"

# === Alpaca LIVE Setup for Options Only ===
ALPACA_API_KEY = "AKQLAH7WUPSEO96MNH7T"  # ⚠️ TEMPORARY: Replace with actual live key
ALPACA_SECRET = "AUzXSxevkdFAGs05xT6NzqNpG0e6bmHfiddjEY1v"  # ⚠️ TEMPORARY: Replace with actual live secret
BASE_URL = "https://api.alpaca.markets"  # Live endpoint for options orders

# ✅ Log Option Trade
def log_option_trade(action, ticker, option_type, strike, expiration, contracts, price, reason):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "ticker": ticker,
        "option_type": option_type,
        "strike": strike,
        "expiration": expiration,
        "contracts": contracts,
        "price": round(price, 4),
        "reason": reason
    }
    try:
        if os.path.exists(OPTION_LOG_FILE):
            with open(OPTION_LOG_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []
        history.append(log_entry)
        with open(OPTION_LOG_FILE, "w") as f:
            json.dump(history, f, indent=4)
        print(f"📝 Logged {action} of {ticker} {option_type} at {price}")
    except Exception as e:
        print(f"⚠️ Failed to log option trade to JSON: {e}")
    try:
        csv_file = OPTION_LOG_FILE.replace(".json", ".csv")
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, 'a', newline='') as csvfile:
            fieldnames = ["timestamp", "action", "ticker", "option_type", "strike", "expiration", "contracts", "price", "reason"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(log_entry)
    except Exception as e:
        print(f"⚠️ Failed to log option trade to CSV: {e}")

# ✅ Submit order to Alpaca Options API
def submit_option_order(symbol, qty, side):
    url = f"{BASE_URL}/v1beta1/options/orders"
    headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET,
        "Content-Type": "application/json"
    }
    payload = {
        "symbol": symbol,
        "qty": qty,
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"✅ Order placed: {symbol}")
    else:
        print(f"❌ Order failed for {symbol}: {response.status_code} - {response.text}")

# === Load signals ===
try:
    with open("filtered_option_signals.json", "r") as f:
        signals = json.load(f)
    print(f"🧠 Loaded {len(signals)} AI-filtered options signals.")
except FileNotFoundError:
    print("⚠️ AI-filtered options not found. Using raw options_signals.json instead.")
    with open("options_signals.json", "r") as f:
        signals = json.load(f)
    print(f"🧠 Loaded {len(signals)} raw option signals.")
# Removed FileNotFoundError block because we're overriding signals above

MAX_PER_TRADE = 50
EST_OPTION_COST_FACTOR = 0.05
SPREAD_PERCENT = 0.10

trade_summary = {"CALL": 0, "PUT": 0}
errors = []
executed = 0

for signal in signals:
    symbol = signal["symbol"]
    direction = signal["direction"]
    source = signal["source"]
    try:
        today = datetime.today()
        days_until_friday = (4 - today.weekday()) % 7
        expiration = today + timedelta(days=days_until_friday)
        if days_until_friday <= 3:
            expiration += timedelta(days=7)
        expiration_str = expiration.strftime("%Y-%m-%d")

        # ✅ NEW: Fetch tradable contracts from contracts endpoint
        contracts_url = f"https://data.alpaca.markets/v1beta1/options/contracts?underlying_symbol={symbol}"
        headers = {
            "APCA-API-KEY-ID": ALPACA_API_KEY,
            "APCA-API-SECRET-KEY": ALPACA_SECRET
        }
        contracts_response = requests.get(contracts_url, headers=headers)
        if contracts_response.status_code != 200:
            raise ValueError(f"Failed to fetch options chain: {contracts_response.text}")
        chain_data = contracts_response.json()
        contracts_data = chain_data.get("contracts", [])

        # 🎯 Filter valid options contracts with ask price and correct OCC format
        # 🎯 Collect final filtered list
        valid_contracts = []
        for c in contracts_data:
            option_symbol = c.get("symbol")
            ask_price = c.get("ask_price", 0)
            if option_symbol and ask_price > 0 and c.get("tradable", False):
                c["option_symbol"] = option_symbol
                c["strike_price"] = c.get("strike_price", 0)
                c["fill_price"] = ask_price
                c["underlying_price"] = c.get("underlying_price", 0)
                valid_contracts.append(c)
            # Removed fallback to snapshot feeds to avoid duplicate/invalid symbols
        # Removed stale leftover line
        # Removed old snapshot logic
        # Removed stale snapshot fallback logic

        # 🎯 Use previously filtered valid contracts (do not reset this list)
        # Removed snapshot contract filtering block

        if not valid_contracts:
            continue  # Try next feed

        selected = valid_contracts[0]  # Pick first valid contract to avoid non-existent symbols
        option_symbol = selected["option_symbol"]
        strike_price = selected["strike_price"]
        fill_price = selected["fill_price"]
        est_cost = fill_price
        qty = max(1, math.floor(MAX_PER_TRADE / est_cost))
        # Removed old fallback loop that was no longer needed
        if not valid_contracts:
            raise ValueError("❌ No valid options found across all feeds")

        print(f"📈 Selected: {option_symbol}, Strike: {strike_price}, Fill: {fill_price}, Qty: {qty}")
        # ✅ Submit and log
        submit_option_order(option_symbol, qty, "buy")

        log_option_trade("BUY", symbol, direction.upper(), strike_price, expiration_str, qty, fill_price, "Matched Valid Contract")
        trade_summary[direction] += 1
        executed += 1
        time.sleep(0.25)

    except Exception as e:
        errors.append((symbol, str(e)))

print(f"\n✅ ORDER EXECUTION COMPLETE: {executed} total option trades logged.")
print("\n📊 Trade Summary:")
for opt, count in trade_summary.items():
    print(f"  {opt}: {count}")
if errors:
    print("\n❌ Errors encountered:")
    for s, msg in errors:
        print(f"  {s}: {msg}")
