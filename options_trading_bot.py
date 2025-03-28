from alpaca.trading.client import TradingClient
from alpaca.trading.requests import ClosePositionRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.live import StockDataStream
from alpaca.data.requests import OptionSnapshotRequest
from alpaca.data.live.option import OptionDataStream
import requests
import json
import os
import csv
from datetime import datetime

API_KEY = os.getenv("APCA_API_KEY_ID")
SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")

client = TradingClient(API_KEY, SECRET_KEY, paper=True)

TRADE_LOG_FILE = "option_trade_log.json"
CSV_REPORT_FILE = "option_trade_log.csv"

# --- Config ---
TAKE_PROFIT_PCT = 0.20
STOP_LOSS_PCT = -0.30

# --- Load open trades ---
if not os.path.exists(TRADE_LOG_FILE):
    print("No trade log found.")
    exit()

with open(TRADE_LOG_FILE, "r") as f:
    trades = json.load(f)

# --- Track open trades only ---
open_trades = [t for t in trades if t["action"] == "BUY"]
if not open_trades:
    print("No open trades to monitor.")
    exit()

# --- Get buying power ---
try:
    account = client.get_account()
    buying_power = float(account.buying_power) * 0.20  # Reserve 20% of capital for options
except Exception as e:
    print(f"⚠️ Unable to fetch account info: {e}")
    buying_power = 0

for trade in open_trades:
    try:
        symbol = trade["ticker"]
        option_symbol = f"{symbol}{trade['expiration'].replace('-', '')}{'C' if trade['option_type'] == 'CALL' else 'P'}{int(float(trade['strike']) * 1000):08d}"

        # --- Get latest market quote ---
        snapshot_url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{symbol}"
        headers = {
            "APCA-API-KEY-ID": API_KEY,
            "APCA-API-SECRET-KEY": SECRET_KEY
        }
        response = requests.get(snapshot_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed snapshot request for {symbol}: {response.status_code}")
            continue

        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON for {symbol} snapshot response.")
            continue

        snapshots = data.get("snapshots", {})

        if option_symbol not in snapshots:
            print(f"🚫 No snapshot returned for {option_symbol}, trying SDK fallback...")
            try:
                contract = client.get_option_contract(option_symbol)
                bid = contract.ask_price or 0
                ask = contract.ask_price or 0
            except Exception as err:
                print(f"❌ Contract fallback failed for {option_symbol}: {err}")
                continue
        else:
            quote = snapshots.get(option_symbol, {}).get("latestQuote", {})
            bid = quote.get("bp")
            ask = quote.get("ap")

        if bid is None or ask is None:
            print(f"❌ Could not get bid/ask for {option_symbol}")
            continue

        # --- Check if there's enough buying power to trade ---
        total_cost = trade["contracts"] * 100 * ((bid + ask) / 2)
        if total_cost > buying_power:
            print(f"💸 Skipping {option_symbol} — Not enough buying power (${buying_power:.2f} < ${total_cost:.2f})")
            continue

        # --- Calculate P&L ---
        current_price = (bid + ask) / 2
        entry_price = trade["price"]
        change_pct = (current_price - entry_price) / entry_price

        max_gain = trade["contracts"] * 100 * entry_price * TAKE_PROFIT_PCT
        max_loss = trade["contracts"] * 100 * entry_price * abs(STOP_LOSS_PCT)

        print(f"🔍 {option_symbol} | Entry: {entry_price} | Now: {current_price:.2f} | Change: {change_pct:.2%}")
        print(f"💰 Max Gain Target: ${max_gain:.2f} | 🚨 Max Risk: ${max_loss:.2f}")

        # --- Check thresholds ---
        if change_pct >= TAKE_PROFIT_PCT:
            reason = "Take Profit"
        elif change_pct <= STOP_LOSS_PCT:
            reason = "Stop Loss"
        else:
            continue

        # --- Close trade (log only for now) ---
        sell_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "SELL",
            "ticker": trade["ticker"],
            "option_type": trade["option_type"],
            "strike": trade["strike"],
            "expiration": trade["expiration"],
            "contracts": trade["contracts"],
            "price": round(current_price, 4),
            "reason": reason,
            "pnl_pct": round(change_pct * 100, 2),
            "outcome": "WIN" if change_pct > 0 else "LOSS"
        }
        trades.append(sell_entry)
        print(f"🚨 SELL triggered: {option_symbol} ({reason})")

    except Exception as e:
        print(f"⚠️ Error while checking trade: {e}")

# --- Save updated log ---
with open(TRADE_LOG_FILE, "w") as f:
    json.dump(trades, f, indent=4)

# --- Export to CSV ---
try:
    with open(CSV_REPORT_FILE, "w", newline="") as csvfile:
        fieldnames = ["timestamp", "action", "ticker", "option_type", "strike", "expiration", "contracts", "price", "reason", "pnl_pct", "outcome"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in trades:
            if row["action"] == "SELL":
                writer.writerow(row)
    print(f"📄 CSV report exported to {CSV_REPORT_FILE}")
except Exception as e:
    print(f"⚠️ Failed to export CSV: {e}")

print("✅ Monitor check complete.")
