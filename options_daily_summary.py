import os
import json
import pandas as pd
from datetime import datetime

positions_path = "options_positions.json"
sales_log_path = "options_sales_log.csv"

# === Load Open Positions ===
open_positions = []
if os.path.exists(positions_path):
    with open(positions_path, "r") as f:
        open_positions = json.load(f)

# === Load Sales Log ===
sales_df = pd.read_csv(sales_log_path) if os.path.exists(sales_log_path) else pd.DataFrame()

# === Summarize Open Positions ===
print("\n====== OPEN POSITIONS ======")
if open_positions:
    total_open = 0
    for pos in open_positions:
        cost = pos["qty"] * pos["estimated_cost_per_contract"]
        total_open += cost
        print(f"{pos['symbol']} ({pos['type']}) | Qty: {pos['qty']} | Cost: ${cost:.2f} | Exp: {pos['expiration']}")
    print(f"\nTotal Open Exposure: ${total_open:.2f}")
else:
    print("No open positions.")

# === Summarize Sales ===
print("\n====== CLOSED TRADES (SALES) ======")
if not sales_df.empty:
    sales_df["timestamp"] = pd.to_datetime(sales_df["timestamp"])
    today = datetime.today().date()
    recent_sales = sales_df[sales_df["timestamp"].dt.date == today]

    total_pnl = sales_df["pnl_percent"].str.replace('%','').astype(float).sum()
    recent_pnl = recent_sales["pnl_percent"].str.replace('%','').astype(float).sum()

    print(f"Total Trades Closed: {len(sales_df)}")
    print(f"Today's Trades Closed: {len(recent_sales)}")
    print(f"Today's PnL: {recent_pnl:.2f}%")
    print(f"Total PnL: {total_pnl:.2f}%")
else:
    print("No sales recorded yet.")
