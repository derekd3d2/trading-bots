import json, csv

with open("option_trade_log.json") as f:
    data = json.load(f)

with open("option_trade_log.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

print("✅ Converted option_trade_log.json → option_trade_log.csv")
