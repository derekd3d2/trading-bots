import os
import json
import alpaca_trade_api as tradeapi
import yfinance as yf
from datetime import datetime, timedelta
import time
import csv

# ✅ Load API Keys
mode = os.getenv("ALPACA_ENV", "paper")
if mode == "paper":
    ALPACA_API_KEY = os.getenv("APCA_PAPER_KEY")
    ALPACA_SECRET_KEY = os.getenv("APCA_PAPER_SECRET")
    ALPACA_BASE_URL = os.getenv("APCA_PAPER_URL", "https://paper-api.alpaca.markets")
else:
    ALPACA_API_KEY = os.getenv("APCA_LIVE_KEY")
    ALPACA_SECRET_KEY = os.getenv("APCA_LIVE_SECRET")
    ALPACA_BASE_URL = os.getenv("APCA_LIVE_URL", "https://api.alpaca.markets")

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    print("❌ API Keys not found! Make sure they are set in ~/.bashrc_custom and sourced correctly.")
    exit()

# ✅ Connect to Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")

# ✅ Trading Strategy Parameters
PROFIT_TARGET = 0.015  # 1.5% profit target
STOP_LOSS = 0.015      # 1.5% stop-loss
CAPITAL_USAGE = 0.75   # 50% of total capital
MAX_TRADES = 15        # Limit trades to top 15 stocks
TRADE_HISTORY_FILE = "/home/ubuntu/trading-bots/trade_history.json"

# ✅ Log Trade
def log_trade(action, ticker, shares, price, reason, prediction=None):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "ticker": ticker,
        "shares": round(shares, 4),
        "price": round(price, 4),
        "reason": reason
    }

    if action == "BUY" and prediction:
        log_entry["prediction"] = prediction

    if action == "SELL":
        try:
            with open(TRADE_HISTORY_FILE, "r") as f:
                full_log = json.load(f)
            for entry in reversed(full_log):
                if entry["action"] == "BUY" and entry["ticker"] == ticker and "prediction" in entry:
                    log_entry["prediction"] = entry["prediction"]
                    break
        except Exception as e:
            print(f"⚠️ Could not backfill prediction for SELL: {e}")
    
    ...


    try:
        if os.path.exists(TRADE_HISTORY_FILE):
            with open(TRADE_HISTORY_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append(log_entry)

        with open(TRADE_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)

        print(f"🖍 Logged {action} of {ticker} at {price}")

        csv_file = TRADE_HISTORY_FILE.replace(".json", ".csv")
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, 'a', newline='') as csvfile:
            fieldnames = ["timestamp", "action", "ticker", "shares", "price", "reason", "prediction"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(log_entry)
    except Exception as e:
        print(f"⚠️ Failed to log trade: {e}")

# ✅ Load AI-Filtered or Raw Trade Signals
def load_trade_signals():
    try:
        with open("filtered_day_signals.json", "r") as file:
            signals = json.load(file)
        print(f"🧑‍🧐 Loaded {len(signals)} AI-filtered WIN signals.")
    except FileNotFoundError:
        print("⚠️ AI-filtered signals not found. Falling back to full signal list.")
        with open("day_trading_signals.json", "r") as file:
            signals = json.load(file)

    sorted_signals = sorted(signals, key=lambda x: x.get("total_score", 0), reverse=True)[:MAX_TRADES]
    return sorted_signals

# ✅ Fetch Current Stock Price
def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        time.sleep(1)
        history = stock.history(period="1d")
        if history.empty:
            return None
        return history["Close"].iloc[-1]
    except Exception as e:
        print(f"❌ Error fetching price for {ticker}: {e}")
        return None

# ✅ Execute Buy Orders with Capital Allocation
def execute_trades():
    account = api.get_account()
    total_equity = float(account.equity)
    allocated_capital = total_equity * CAPITAL_USAGE
    print(f"[INFO] Allocating ${allocated_capital:.2f} for day trading (75% of ${total_equity})")

    trade_signals = load_trade_signals()
    if not trade_signals:
        print("⚠️ No trades to execute.")
        return

    capital_per_stock = allocated_capital / len(trade_signals)
    open_positions = {pos.symbol for pos in api.list_positions()}

    for trade in trade_signals:
        ticker = trade["ticker"]
        if ticker in open_positions:
            print(f"⚠️ Skipping {ticker}: Already in position.")
            continue

        current_price = get_stock_price(ticker)
        if current_price is None:
            continue

        shares_to_buy = capital_per_stock / current_price
        asset = api.get_asset(ticker)
        if shares_to_buy < 1 and not asset.fractionable:
            print(f"⚠️ Skipping {ticker}: Not fractionable, insufficient capital for 1 whole share.")
            continue

        print(f"🚀 Buying {shares_to_buy:.4f} shares of {ticker} at {current_price}")
        try:
            api.submit_order(
                symbol=ticker,
                qty=round(shares_to_buy) if not asset.fractionable else shares_to_buy,
                side="buy",
                type="market",
                time_in_force="day"
            )
            log_trade("BUY", ticker, shares_to_buy, current_price, "New Signal", prediction=trade.get("ml_prediction"))
        except Exception as e:
            print(f"❌ Error executing buy for {ticker}: {e}")

# ✅ Execute Sell Logic
def check_and_sell_positions():
    positions = api.list_positions()

    for pos in positions:
        ticker = pos.symbol
        position_qty = float(pos.qty)
        if position_qty <= 0:
            print(f"⚠️ Skipping {ticker}: no shares held.")
            continue

        buy_price = float(pos.avg_entry_price)
        current_price = get_stock_price(ticker)
        if current_price is None:
            continue

        price_change = (current_price - buy_price) / buy_price

        if price_change >= PROFIT_TARGET or price_change <= -STOP_LOSS:
            open_orders = api.list_orders(status='open', symbols=[ticker])
            if open_orders:
                print(f"⚠️ Skipping selling {ticker}: open order detected.")
                continue

            try:
                api.submit_order(
                    symbol=ticker,
                    qty=position_qty,
                    side="sell",
                    type="market",
                    time_in_force="day"
                )
                reason = "Target hit" if price_change >= PROFIT_TARGET else "Stop-loss triggered"
                log_trade("SELL", ticker, position_qty, current_price, reason)
                print(f"✅ Selling {ticker} due to {reason}.")
            except Exception as e:
                print(f"❌ Error executing sell for {ticker}: {e}")

# ✅ Strategy Execution
if __name__ == "__main__":
    execute_trades()
    check_and_sell_positions()
    print("✅ Day trading execution complete.")
