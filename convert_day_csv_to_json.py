import csv
import json
import os

CSV_FILENAME = "trade_history.csv"
JSON_FILENAME = "day_trade_log.json"

def convert_csv_to_json():
    # Check if JSON file already exists; if yes, back it up to avoid data loss
    if os.path.exists(JSON_FILENAME):
        os.rename(JSON_FILENAME, JSON_FILENAME + ".backup")
        print(f"Existing {JSON_FILENAME} backed up as {JSON_FILENAME}.backup")

    trades = []

    # Read CSV and convert rows to JSON
    with open(CSV_FILENAME, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # CSV columns based on your provided sample data:
            # [timestamp, action, ticker, shares, price, reason]
            trade = {
                "timestamp": row[0],
                "action": row[1],
                "ticker": row[2],
                "shares": float(row[3]),
                "price": float(row[4]),
                "reason": row[5]
            }
            trades.append(trade)

    # Write to JSON file
    with open(JSON_FILENAME, 'w') as jsonfile:
        json.dump(trades, jsonfile, indent=4)

    print(f"Successfully converted {CSV_FILENAME} to {JSON_FILENAME}")

if __name__ == "__main__":
    convert_csv_to_json()
