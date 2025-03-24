import os
import json
from collections import defaultdict

# Input signal files from each strategy
input_files = [
    "options_congress_signals.json",
    "options_insider_signals.json",
    "options_gov_signals.json",
    "options_wsb_signals.json"
]

# Track signals and their source files
signal_tracker = defaultdict(lambda: {"sources": set(), "entries": []})

# Load all signals and group by (symbol, direction)
for file in input_files:
    if os.path.exists(file):
        with open(file, "r") as f:
            try:
                signals = json.load(f)
                for entry in signals:
                    key = (entry["symbol"], entry["direction"])
                    signal_tracker[key]["sources"].add(file)
                    signal_tracker[key]["entries"].append(entry)
                print(f"✅ Loaded {len(signals)} signals from {file}")
            except json.JSONDecodeError:
                print(f"⚠️ Skipped {file} due to invalid JSON.")
    else:
        print(f"⚠️ File not found: {file}")

# Keep only entries that appear in 2 or more unique source files
validated_signals = []
for key, value in signal_tracker.items():
    if len(value["sources"]) >= 2:
        validated_signals.extend(value["entries"])

# Save to final merged and validated output
if validated_signals:
    with open("options_signals.json", "w") as f:
        json.dump(validated_signals, f, indent=2)
    print(f"\n✅ Saved {len(validated_signals)} cross-validated signals to options_signals.json")
else:
    print("\n⚠️ No cross-validated signals found. Check your input files.")
