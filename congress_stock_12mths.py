import os
import pandas as pd
import requests
from datetime import datetime, timedelta

# === CONFIG ===
API_KEY = os.getenv("QUIVER_API_KEY")  # make sure this is set in your ~/.bashrc_custom
headers = {"Authorization": f"Bearer {API_KEY}"}
url = "https://api.quiverquant.com/beta/bulk/congresstrading"

# === Fetch + Process ===
r = requests.get(url, headers=headers)
df = pd.DataFrame(r.json())
df["TransactionDate"] = pd.to_datetime(df["TransactionDate"])

# Filter for last 12 months and stock-only trades
last_year = datetime.now() - timedelta(days=365)
df = df[(df["TransactionDate"] > last_year) & ~df["Description"].str.lower().str.contains("option")]
df = df[df["Transaction"].isin(["Purchase", "Sale"])]

# Save to CSV
df = df[["Representative", "TransactionDate", "Ticker", "Transaction", "Range", "Party", "House", "Description"]]
df.to_csv("congress_trades_last_12mo.csv", index=False)
print("✅ Exported to congress_trades_last_12mo.csv")
