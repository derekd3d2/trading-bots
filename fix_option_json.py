import json

INPUT_FILE = "option_trade_log.json"
OUTPUT_FILE = "option_trade_log_fixed.json"

with open(INPUT_FILE, "r") as f:
    data = json.load(f)

for entry in data:
    if entry["action"] == "BUY" and "sentiment" not in entry:
        if entry["option_type"].upper() == "CALL":
            entry["sentiment"] = "bullish"
        elif entry["option_type"].upper() == "PUT":
            entry["sentiment"] = "bearish"
        else:
            entry["sentiment"] = "unknown"

with open(OUTPUT_FILE, "w") as f:
    json.dump(data, f, indent=4)

print("✅ All BUY entries updated with sentiment. Saved to option_trade_log_fixed.json.")
