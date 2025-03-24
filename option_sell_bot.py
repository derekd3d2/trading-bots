import os
import json
import time
from datetime import datetime, timedelta
from alpaca_trade_api.rest import REST
import csv

OPTION_LOG_FILE = "option_trade_log.json"

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

    # Write to JSON
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

    # Write to CSV
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


# === Alpaca Setup ===
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
alpaca = REST(ALPACA_API_KEY, ALPACA_SECRET, BASE_URL)

# === Load Open Positions ===
if not os.path.exists("options_positions.json"):
    print("No open positions to manage.")
    exit()

with open("options_positions.json", "r") as f:
    open_positions = json.load(f)

# === Management Settings ===
TAKE_PROFIT = 0.25  # +25%
STOP_LOSS = -0.50   # -50%
EXPIRY_WINDOW = 3   # exit if option expires in 3 days or less

updated_positions = []
for position in open_positions:
    symbol = position["symbol"]
    strike = position["strike"]
    expiration = datetime.strptime(position["expiration"], "%Y-%m-%d")
    qty = position["qty"]
    entry_price = position.get("fill_price") or position["estimated_cost_per_contract"]

    try:
        trade = alpaca.get_latest_trade(symbol)
        current_price = float(trade.price)

        # Estimate option PnL
        change = (current_price - entry_price) / entry_price
        pnl = round(change, 4)
        days_to_expiry = (expiration - datetime.now()).days

        reason = None
        if pnl >= TAKE_PROFIT:
            reason = "Take Profit"
        elif pnl <= STOP_LOSS:
            reason = "Stop Loss"
        elif days_to_expiry <= EXPIRY_WINDOW:
            reason = "Expiring Soon"

        if reason:
            log_option_trade(
                action="SELL",
                ticker=symbol,
                option_type=position.get("type", "CALL"),  # Use 'type' to match how direction is stored
                strike=strike,
                expiration=expiration.date().isoformat(),
                contracts=qty,
                price=current_price,
                reason=reason
            )
            print(f"✅ SOLD: {symbol} ({reason})")
        else:
            updated_positions.append(position)

    except Exception as e:
        print(f"❌ Error checking {symbol}: {e}")
        updated_positions.append(position)

# === Save Remaining Open Positions ===
with open("options_positions.json", "w") as f:
    json.dump(updated_positions, f, indent=2)

print("\n✅ Sell check complete.")
