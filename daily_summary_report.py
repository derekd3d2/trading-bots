import os
import json
import csv
from datetime import datetime, date
from alpaca_trade_api.rest import REST

APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
APCA_BASE_URL = os.getenv("APCA_PAPER_URL", "https://paper-api.alpaca.markets")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
APCA_BASE_URL = os.getenv("APCA_PAPER_URL", "https://paper-api.alpaca.markets")
api = REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_BASE_URL)

TRADE_LOG = "trade_history.csv"
OPTION_LOG = "option_trade_log.csv"
POSITION_FILE = "options_positions.json"
SUMMARY_FILE = f"daily_summary_{date.today()}.txt"

def get_account_values():
    account = api.get_account()
    return float(account.cash), float(account.portfolio_value)

def generate_summary():
    cash, portfolio = get_account_values()
    with open(SUMMARY_FILE, "w") as f:
        f.write(f"📊 DAILY SUMMARY — {date.today()} 📊\n\n")
        f.write(f"Cash Balance: ${cash:,.2f}\n")
        f.write(f"Portfolio Value: ${portfolio:,.2f}\n")
        f.write("\n(This is a placeholder. Full logic coming soon.)\n")

    print(f"✅ Summary written to {SUMMARY_FILE}")

if __name__ == "__main__":
    generate_summary()
