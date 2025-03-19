import json
import os
import time
from datetime import datetime, timedelta

# Load signals from individual bots, handling different filenames

def load_signals(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as file:
        return json.load(file)

# Combine signals uniquely and remove duplicates clearly by ticker

def combine_signals():
    filenames = ['insider_signals.json', 'congress_signals.json', 'twitter_signals.json', 'wsb_signals.json']

    combined_signals = {}
    for filename in filenames:
        signals = load_signals(filename)
        for signal in signals:
            ticker = signal['ticker']
            if ticker not in combined_signals:
                combined_signals[ticker] = signal

    return combined_signals

# Save combined signals to JSON

def save_combined_signals(signals, filename='day_trading_signals.json'):
    trade_signals = list(signals.values())

    with open(filename, 'w') as f:
        json.dump(trade_signals, f, indent=4)
    print(f"✅ {len(trade_signals)} unique trade signals saved to {filename}")

# Continuous execution every 5 minutes during market hours

def run_signal_bot():
    end_of_day = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)

    while datetime.now() < end_of_day:
        print(f"📊 Running signal generation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        combined_signals = combine_signals()
        save_combined_signals(combined_signals)
        print("🕑 Waiting 5 minutes before next run.")
        time.sleep(300)

if __name__ == "__main__":
    run_signal_bot()
