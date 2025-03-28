import json

INPUT_FILE = "option_trade_log.json"
OUTPUT_FILE = "option_trade_log.json"

with open(INPUT_FILE, "r") as f:
    trades = json.load(f)

for t in trades:
    if t["action"] == "SELL":
        pnl = t.get("pnl_pct", 0)
        t["outcome"] = "WIN" if pnl > 0 else "LOSS"
        t.setdefault("prediction", "unknown")

with open(OUTPUT_FILE, "w") as f:
    json.dump(trades, f, indent=2)

print(f"✅ Labeled SELL trades with outcome + prediction.")
