import os
import json
import requests

TRADE_LOG_FILE = "option_trade_log.json"
DATA_API_KEY = os.getenv("APCA_LIVE_KEY")
DATA_SECRET_KEY = os.getenv("APCA_LIVE_SECRET")

if not os.path.exists(TRADE_LOG_FILE):
    print("❌ No trade log found.")
    exit()

with open(TRADE_LOG_FILE, "r") as f:
    trades = json.load(f)

open_trades = [t for t in trades if t["action"] == "BUY"]
if not open_trades:
    print("📭 No open trades to check.")
    exit()

headers = {
    "APCA-API-KEY-ID": DATA_API_KEY,
    "APCA-API-SECRET-KEY": DATA_SECRET_KEY
}

option_chains = {}
missing_contracts = []

for trade in open_trades:
    symbol = trade["ticker"].upper()
    option_symbol = f"{symbol}{trade['expiration'].replace('-', '')}{'C' if trade['option_type'] == 'CALL' else 'P'}{int(float(trade['strike']) * 1000):08d}"

    if symbol not in option_chains:
        url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{symbol}"
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            option_chains[symbol] = set(data.get("snapshots", {}).keys())
            print(f"🔁 Retrieved {len(option_chains[symbol])} snapshot contracts for {symbol}")
        except Exception as e:
            print(f"⚠️ Error fetching snapshots for {symbol}: {e}")
            option_chains[symbol] = set()

    if option_symbol in option_chains[symbol]:
        print(f"✅ {option_symbol} found in snapshot")
    else:
        print(f"❌ {option_symbol} NOT FOUND")
        missing_contracts.append(option_symbol)

if missing_contracts:
    with open("bad_contracts.json", "w") as f:
        json.dump(sorted(set(missing_contracts)), f, indent=2)
    print("\n🚫 Missing contracts saved to bad_contracts.json")
else:
    print("\n✅ All contracts are valid.")
