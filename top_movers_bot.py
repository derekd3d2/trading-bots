import requests
import pandas as pd
import json
from datetime import datetime

TOP_MOVERS_FILE = "/home/ubuntu/trading-bots/top_movers_signals.json"

def fetch_top_movers():
    url = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers,ta_toplosers&o=-change"
    tables = pd.read_html(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text)

    df = tables[-2]  # typically the second last table contains the data
    df.columns = df.iloc[0]
    df = df[1:]

    movers = []

    for _, row in df.iterrows():
        ticker = row['Ticker']
        change = float(row['Change'].replace('%', '').replace('+', ''))
        volume = int(row['Volume'].replace(',', ''))
        float_size = row['Float']
        float_multiplier = {'M': 1e6, 'K': 1e3, 'B': 1e9}
        float_num = float(float_size[:-1]) * float_multiplier.get(float_size[-1], 1)

        movers.append({
            'ticker': ticker,
            'change': change,
            'volume': volume,
            'float': float_num,
            'action': 'SHORT' if change > 80 else 'LONG' if change < -30 else 'NONE'
        })

    # Filter out any 'NONE' actions
    movers = [m for m in movers if m['action'] != 'NONE']

    # Save to JSON
    with open(TOP_MOVERS_FILE, "w") as f:
        json.dump(movers, f, indent=2)

    print(f"✅ Saved {len(movers)} top movers signals.")

if __name__ == "__main__":
    fetch_top_movers()
