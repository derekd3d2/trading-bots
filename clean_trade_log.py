import json
import os

TRADE_LOG_FILE = "option_trade_log.json"
BAD_CONTRACTS_FILE = "bad_contracts.json"
OUTPUT_FILE = "option_trade_log_cleaned.json"

if not os.path.exists(TRADE_LOG_FILE):
    print("❌ Trade log not found.")
    exit()

if not os.path.exists(BAD_CONTRACTS_FILE):
    print("❌ bad_contracts.json not found. Run test_option_sync.py first.")
    exit()

with open(TRADE_LOG_FILE, "r") as f:
    trades = json.load(f)

with open(BAD_CONTRACTS_FILE, "r") as f:
    bad_contracts = set(json.load(f))

cleaned = []
removed = 0

for trade in trades:
    symbol = trade["ticker"]
    option_symbol = f"{symbol}{trade['expiration'].replace('-', '')}{'C' if trade['option_type'] == 'CALL' else 'P'}{int(float(trade['strike']) * 1000):08d}"
    if trade["action"] == "BUY" and option_symbol in bad_contracts:
        removed += 1
        continue
    cleaned.append(trade)

with open(OUTPUT_FILE, "w") as f:
    json.dump(cleaned, f, indent=2)

print(f"✅ Cleaned trade log saved to {OUTPUT_FILE}")
print(f"🧹 Removed {removed} bad BUY trades from the log.")
