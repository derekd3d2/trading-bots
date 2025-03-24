import os
import json
import csv
from datetime import datetime, date
from alpaca_trade_api.rest import REST

# === Alpaca API Setup ===
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
api = REST(ALPACA_API_KEY, ALPACA_SECRET, BASE_URL)

# === Config ===
TRADE_LOG = "trade_history.csv"
OPTION_LOG = "option_trade_log.csv"
POSITION_FILE = "options_positions.json"
SUMMARY_FILE = f"daily_summary_{date.today()}.txt"

# === Load Trade History ===
def load_csv_trades(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        return [row for row in reader if row['timestamp'].startswith(str(date.today()))]

# === Load Options Positions ===
def load_open_positions():
    if not os.path.exists(POSITION_FILE):
        return []
    with open(POSITION_FILE, "r") as f:
        return json.load(f)

# === Calculate Current Option PnL ===
def calculate_option_pnl(positions):
    option_details = []
    total_value = 0
    for pos in positions:
        symbol = pos["symbol"]
        contracts = float(pos["qty"])
        fill_price = float(pos.get("fill_price") or pos["estimated_cost_per_contract"])
        try:
            trade = api.get_latest_trade(symbol)
            current_price = float(trade.price)
            change = (current_price - fill_price) / fill_price
            total_value += current_price * contracts
            option_details.append((symbol, fill_price, current_price, round(change * 100, 2), contracts))
        except:
            continue
    return option_details, total_value

# === Get Alpaca Cash ===
def get_alpaca_balance():
    account = api.get_account()
    return float(account.cash), float(account.portfolio_value)

# === Main Summary ===
def generate_summary():
    trades = load_csv_trades(TRADE_LOG)
    option_trades = load_csv_trades(OPTION_LOG)
    open_options = load_open_positions()
    options_pnl, open_option_value = calculate_option_pnl(open_options)
    alpaca_cash, alpaca_portfolio = get_alpaca_balance()

    # === Beginning balances (for now, we use portfolio as starting point)
    beginning_balance = alpaca_portfolio  # placeholder assumption
    longs, shorts, options = 0, 0, open_option_value

    # === Trade activity ===
    stock_buys = [t for t in trades if t["action"] == "BUY"]
    stock_sells = [t for t in trades if t["action"] == "SELL"]
    option_buys = [t for t in option_trades if t["action"] == "BUY"]
    option_sells = [t for t in option_trades if t["action"] == "SELL"]

    # === Output Summary ===
    with open(SUMMARY_FILE, "w") as f:
        f.write(f"===== DAILY TRADING SUMMARY ({date.today()}) =====\n\n")
        f.write(f"Beginning Balance (Est.): ${beginning_balance:,.2f}\n")
        f.write(f"- Longs: ${longs:,.2f}  Shorts: ${shorts:,.2f}  Options: ${options:,.2f}\n\n")

        f.write(f"🟩 Stock Activity:\n")
        f.write(f"  Buys: {len(stock_buys)} totaling ${sum(float(t['price']) * float(t['shares']) for t in stock_buys):,.2f}\n")
        f.write(f"  Sells: {len(stock_sells)} totaling ${sum(float(t['price']) * float(t['shares']) for t in stock_sells):,.2f}\n\n")

        f.write(f"🟦 Option Activity:\n")
        f.write(f"  Buys: {len(option_buys)} totaling ${sum(float(t['price']) * float(t['contracts']) for t in option_buys):,.2f}\n")
        f.write(f"  Sells: {len(option_sells)} totaling ${sum(float(t['price']) * float(t['contracts']) for t in option_sells):,.2f}\n\n")

        f.write(f"📈 Open Option Positions:\n")
        for sym, fill, current, change, qty in options_pnl:
            f.write(f"  {sym}: {qty} contracts | Entry: ${fill} → Now: ${current} ({change}%)\n")

        f.write(f"\n💰 Ending Cash Balance: ${alpaca_cash:,.2f}\n")
        f.write(f"📊 Ending Portfolio Value: ${alpaca_portfolio:,.2f}\n")
        f.write(f"=============================================\n")

    print(f"✅ Daily summary written to {SUMMARY_FILE}")

if __name__ == "__main__":
    generate_summary()
