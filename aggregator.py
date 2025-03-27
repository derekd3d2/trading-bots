#!/usr/bin/env python3
"""
aggregator.py

Reads the outputs from multiple gatherer scripts (ms_congress.py, ms_insider_trading.py, etc.)
and merges them into a single JSON file (all_signals.json). Also produces specialized outputs:

- day_trading_signals.json for your day trading bot
- short_signals.json for your short trading bot

Usage:
  python3 aggregator.py
"""

import os
import json
from datetime import datetime

# ---------------------------------------------------------------------------
# 1. HELPER: Safe JSON Loading
# ---------------------------------------------------------------------------
def load_json(filepath):
    """
    Utility to load JSON safely. Returns empty list/dict if file missing or invalid.
    """
    if not os.path.exists(filepath):
        print(f"⚠️  {filepath} not found. Returning empty structure.")
        return None

    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠️  Could not parse {filepath}: {e}")
        return None


# ---------------------------------------------------------------------------
# 2. READ GATHERER OUTPUTS
#    (You can rename these as needed to match your actual file paths.)
# ---------------------------------------------------------------------------
BASE_DIR = os.getcwd()

congress_path = os.path.join(BASE_DIR, "congress_signals.json")        # from ms_congress.py
insider_path  = os.path.join(BASE_DIR, "ms_insider_signals.json")     # from ms_insider_trading.py
wsb_path      = os.path.join(BASE_DIR, "ms_wsb_signals.json")         # from ms_wsb.py
gov_path      = os.path.join(BASE_DIR, "ms_gov_signals.json")         # from ms_gov.py

congress_data = load_json(congress_path) or {}
insider_data  = load_json(insider_path)  or {}
wsb_data      = load_json(wsb_path)      or {}
gov_data      = load_json(gov_path)      or {}

# 
# Each gatherer script can produce slightly different structures. For example:
# ms_congress.py => { "buy_signals": [...], "short_signals": [...], "options_signals": [...] }
# ms_insider_trading.py => { "buy_signals": [...], "short_signals": [...] }
# ms_wsb_signals.json => { "buy_signals": [...] }
# ms_gov_signals.json => { "buy_signals": [...] }
#
# We'll store them in a single dictionary named 'all_signals', grouping by category:
#

all_signals = {
    "congress_buy":    congress_data.get("buy_signals", []),
    "congress_short":  congress_data.get("short_signals", []),
    "congress_options":congress_data.get("options_signals", []),

    "insider_buy":     insider_data.get("buy_signals", []),
    "insider_short":   insider_data.get("short_signals", []),

    "wsb_buy":         wsb_data.get("buy_signals", []),

    "gov_buy":         gov_data.get("buy_signals", [])
}

# ---------------------------------------------------------------------------
# 3. COMBINE INTO a SINGLE "all_signals.json"
# ---------------------------------------------------------------------------
all_signals_path = os.path.join(BASE_DIR, "all_signals.json")
with open(all_signals_path, "w") as f:
    json.dump(all_signals, f, indent=2)
print(f"✅ Merged all data → {all_signals_path}")

# ---------------------------------------------------------------------------
# 4. GENERATE day_trading_signals.json
#    (Equivalent to your ms_daytrading_signals.py logic)
#
# A typical approach is to weigh or combine the different data sources
# to decide which tickers are good "long/day" candidates.
# Below is a simplified example showing how you might unify them:
# ---------------------------------------------------------------------------

def normalize_score(score, cap=10):
    """
    Example of normalizing any numeric 'score' to a 0-10 range.
    Adjust this function if you have more complex weighting.
    """
    try:
        val = float(score)
        return min(val, cap)
    except:
        return 0.0

def build_day_trading_signals():
    """
    Example logic to combine insider + congress + WSB + gov signals
    into a single day_trading_signals.json.
    """
    day_signals = {}

    # We'll gather buy signals from each feed and add them up.
    # Then produce a single 'score' for each ticker.

    # 1) Congress (buy_signals)
    for entry in all_signals["congress_buy"]:
        ticker = entry.get("ticker", "").upper()
        score  = entry.get("congress_score", 1)
        day_signals.setdefault(ticker, 0)
        day_signals[ticker] += normalize_score(score, 10) * 0.4  # 40% weight

    # 2) Insider (buy_signals)
    for entry in all_signals["insider_buy"]:
        ticker = entry.get("ticker", "").upper()
        score  = entry.get("insider_score", 1)
        day_signals.setdefault(ticker, 0)
        day_signals[ticker] += normalize_score(score, 10) * 0.3  # 30% weight

    # 3) WSB
    for entry in all_signals["wsb_buy"]:
        ticker = entry.get("ticker", "").upper()
        score  = entry.get("wsb_score", 1)
        day_signals.setdefault(ticker, 0)
        day_signals[ticker] += normalize_score(score, 10) * 0.2  # 20% weight

    # 4) Gov
    for entry in all_signals["gov_buy"]:
        ticker = entry.get("ticker", "").upper()
        score  = entry.get("gov_score", 1)
        day_signals.setdefault(ticker, 0)
        day_signals[ticker] += normalize_score(score, 10) * 0.1  # 10% weight

    # Filter out low total scores
    final_day_signals = []
    for ticker, total_score in day_signals.items():
        if total_score < 1.0:
            continue
        final_day_signals.append({"ticker": ticker, "total_score": round(total_score, 2)})

    # Sort descending
    final_day_signals.sort(key=lambda x: x["total_score"], reverse=True)

    return final_day_signals

day_signals = build_day_trading_signals()
day_signals_path = os.path.join(BASE_DIR, "day_trading_signals.json")
with open(day_signals_path, "w") as f:
    json.dump(day_signals, f, indent=2)
print(f"✅ Created day_trading_signals.json with {len(day_signals)} entries.")

# ---------------------------------------------------------------------------
# 5. GENERATE short_signals.json
#    (Equivalent to your ms_short_signals.py logic)
#
# We'll combine the "short_signals" blocks from each feed
# (congress_short, insider_short, etc.). Optionally, you can parse negative WSB signals.
# ---------------------------------------------------------------------------
def build_short_signals():
    short_map = {}

    # 1) Congress short_signals
    for entry in all_signals["congress_short"]:
        ticker = entry.get("ticker", "").upper()
        score  = entry.get("short_score", 1)
        short_map[ticker] = short_map.get(ticker, 0) + score

    # 2) Insider short_signals
    for entry in all_signals["insider_short"]:
        ticker = entry.get("ticker", "").upper()
        score  = entry.get("short_score", 1)
        short_map[ticker] = short_map.get(ticker, 0) + score

    # 3) Potential negative WSB (not in your final code yet, but if you'd want it):
    #    e.g. if wsb_score < 0 => add to short
    # For now, we'll skip because your ms_wsb_signals only has buy_signals with positive score.

    # Filter out very low scores if you want
    short_signals_list = []
    for ticker, sscore in short_map.items():
        if sscore <= 0:
            continue
        short_signals_list.append({"ticker": ticker, "short_score": round(sscore, 2)})

    # Sort descending by short_score
    short_signals_list.sort(key=lambda x: x["short_score"], reverse=True)
    return short_signals_list

final_shorts = build_short_signals()
short_signals_path = os.path.join(BASE_DIR, "short_signals.json")
with open(short_signals_path, "w") as f:
    json.dump(final_shorts, f, indent=2)
print(f"✅ Created short_signals.json with {len(final_shorts)} entries.")


print("\n✅ aggregator.py complete.")
